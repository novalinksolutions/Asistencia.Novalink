import reflex as rx
import hashlib
import logging
from sqlalchemy import text
from app.states.database_state import DatabaseState
from app.states.base_state import BaseState


class HeaderState(DatabaseState):
    show_dropdown: bool = False
    show_password_modal: bool = False
    current_password: str = ""
    new_password: str = ""
    confirm_password: str = ""
    is_loading: bool = False

    @rx.event
    def toggle_dropdown(self):
        self.show_dropdown = not self.show_dropdown

    @rx.event
    def close_dropdown(self):
        self.show_dropdown = False

    @rx.event
    def open_password_modal(self):
        self.show_dropdown = False
        self.current_password = ""
        self.new_password = ""
        self.confirm_password = ""
        self.show_password_modal = True

    @rx.event
    async def close_password_modal(self):
        self.show_password_modal = False
        base_state = await self.get_state(BaseState)
        base_state.force_password_change_on_login = False

    @rx.event
    async def logout(self):
        """Clear session and redirect to login."""
        logging.info("Initiating logout sequence")
        base_state = await self.get_state(BaseState)
        await base_state.close_session()
        base_state.logged_user_id = 0
        base_state.logged_user_name = ""
        base_state.logged_user_description = ""
        base_state.current_company_name = ""
        base_state.current_database_name = "novalink"
        base_state.active_page = ""
        base_state.force_password_change_on_login = False
        base_state.password_expired_message = ""
        from app.states.login_state import LoginState

        login_state = await self.get_state(LoginState)
        login_state.empresa = ""
        login_state.search_text = ""
        login_state.username = ""
        login_state.password = ""
        login_state.error_message = ""
        login_state.show_suggestions = False
        login_state.is_loading = False
        self.show_dropdown = False
        return rx.redirect("/login")

    @rx.event
    async def change_password(self):
        """Handle password change submission."""
        if (
            not self.current_password
            or not self.new_password
            or (not self.confirm_password)
        ):
            return rx.toast.error("Todos los campos son obligatorios.")
        if self.new_password != self.confirm_password:
            return rx.toast.error("las contraseñas nuevas no coinciden.")
        if len(self.new_password) < 4:
            return rx.toast.error("La nueva contraseña es muy corta.")
        self.is_loading = True
        base_state = await self.get_state(BaseState)
        user_id = base_state.logged_user_id
        if not user_id:
            self.is_loading = False
            return rx.toast.error(
                "Error de sesión. Por favor inicie sesión nuevamente."
            )
        try:
            query = "SELECT pwd FROM public.usuarios WHERE id = :id"
            results = await self._execute_query(query, {"id": user_id})
            if not results:
                self.is_loading = False
                return rx.toast.error("Usuario no encontrado.")
            stored_hash = results[0]["pwd"]
            current_hash = hashlib.sha256(self.current_password.encode()).hexdigest()
            if current_hash != stored_hash:
                self.is_loading = False
                return rx.toast.error("La contraseña actual es incorrecta.")
            new_hash = hashlib.sha256(self.new_password.encode()).hexdigest()
            update_query = """
                UPDATE public.usuarios 
                SET 
                    pwd = :pwd, 
                    cambiarpwd = false,
                    fechacambiopwd = NOW(),
                    usuariomodifica = :id,
                    fechamodificacion = NOW()
                WHERE id = :id
            """
            await self._execute_write(update_query, {"id": user_id, "pwd": new_hash})
            base_state.force_password_change_on_login = False
            base_state.password_expired_message = ""
            self.is_loading = False
            self.show_password_modal = False
            return rx.toast.success("Contraseña actualizada correctamente.")
        except Exception as e:
            logging.exception(f"Error changing password: {e}")
            self.is_loading = False
            return rx.toast.error("Error al actualizar la contraseña.")