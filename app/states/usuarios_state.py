import reflex as rx
from typing import TypedDict, Optional
import hashlib
import logging
import time
from sqlalchemy import text
from app.states.database_state import DatabaseState


class User(TypedDict):
    id: int
    name: str
    description: str
    profile_id: int
    active: bool
    force_password_change: bool
    password_expires: bool


class UsuariosState(DatabaseState):
    users: list[User] = []
    search_query: str = ""
    show_inactive: bool = False
    show_modal: bool = False
    is_editing: bool = False
    modal_user: User = {
        "id": 0,
        "name": "",
        "description": "",
        "profile_id": 1,
        "active": True,
        "force_password_change": False,
        "password_expires": False,
    }
    show_delete_confirm: bool = False
    user_to_delete: Optional[User] = None
    _last_error_timestamp: float = 0.0

    async def _check_table_exists(self) -> bool:
        """Check if public.usuarios table exists in current database."""
        try:
            query = """
                SELECT EXISTS (
                   SELECT FROM information_schema.tables 
                   WHERE  table_schema = 'public'
                   AND    table_name   = 'usuarios'
                ) as exists
            """
            results = await self._execute_query(query)
            return bool(results and results[0]["exists"])
        except Exception as e:
            logging.exception(f"Error checking table existence: {e}")
            return False

    @rx.event
    async def on_load(self):
        """Load users from database on page load."""
        await self.load_users()

    @rx.event
    async def load_users(self):
        """Load users from public.usuarios table."""
        if not await self._check_table_exists():
            current_time = time.time()
            if current_time - self._last_error_timestamp < 2.0:
                return
            self._last_error_timestamp = current_time
            from app.states.base_state import BaseState

            base_state = await self.get_state(BaseState)
            db_name = base_state.current_database_name
            self.users = []
            return rx.toast.error(
                f"⚠️ La tabla 'usuarios' no existe en la base de datos '{db_name}'. Por favor inicie sesión seleccionando 'Corporación Novalink'.",
                duration=8000,
                close_button=True,
            )
        try:
            query = """
                SELECT 
                    id,
                    nombre as name,
                    descripcion as description,
                    perfil as profile_id,
                    activo as active,
                    cambiarpwd as force_password_change,
                    caducapwd as password_expires
                FROM public.usuarios 
                WHERE id > 0
                ORDER BY nombre ASC
            """
            results = await self._execute_query(query)
            self.users = [
                User(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"] or "",
                    profile_id=row["profile_id"],
                    active=bool(row["active"]),
                    force_password_change=bool(row["force_password_change"]),
                    password_expires=bool(row["password_expires"]),
                )
                for row in results
            ]
        except Exception as e:
            logging.exception(f"Error loading users: {e}")
            self.users = []

    @rx.var
    def filtered_users(self) -> list[User]:
        filtered = self.users
        if not self.show_inactive:
            filtered = [u for u in filtered if u["active"]]
        if not self.search_query.strip():
            return filtered
        query = self.search_query.lower()
        return [
            u
            for u in filtered
            if query in u["name"].lower() or query in u["description"].lower()
        ]

    def _get_empty_user(self) -> User:
        return {
            "id": 0,
            "name": "",
            "description": "",
            "profile_id": 1,
            "active": True,
            "force_password_change": False,
            "password_expires": False,
        }

    @rx.event
    def set_search_query(self, value: str):
        self.search_query = value

    @rx.event
    def set_show_inactive(self, value: bool):
        self.show_inactive = value

    @rx.event
    def open_add_modal(self):
        self.is_editing = False
        self.modal_user = self._get_empty_user()
        self.show_modal = True

    @rx.event
    def open_edit_modal(self, user: User):
        self.is_editing = True
        self.modal_user = user
        self.show_modal = True

    @rx.event
    def close_modal(self):
        self.show_modal = False

    @rx.event
    async def check_username_exists(self, name: str, exclude_id: int = 0) -> bool:
        """Check if a username already exists."""
        query = (
            "SELECT 1 FROM public.usuarios WHERE nombre = :name AND id != :id LIMIT 1"
        )
        results = await self._execute_query(query, {"name": name, "id": exclude_id})
        return len(results) > 0

    @rx.event
    async def reset_user_password(self):
        """Reset current modal user password to default '12345678'."""
        if not self.is_editing or not self.modal_user["id"]:
            return
        try:
            user_id = self.modal_user["id"]
            default_pwd_hash = hashlib.sha256("12345678".encode()).hexdigest()
            query = """
                UPDATE public.usuarios 
                SET 
                    pwd = :pwd,
                    cambiarpwd = true,
                    fechacambiopwd = NOW(),
                    usuariomodifica = 1,
                    fechamodificacion = NOW()
                WHERE id = :id
            """
            await self._execute_write(query, {"id": user_id, "pwd": default_pwd_hash})
            yield rx.toast.success("Contraseña restablecida a '12345678' correctamente")
        except Exception as e:
            logging.exception(f"Error resetting password: {e}")
            yield rx.toast.error("Error al restablecer contraseña")

    @rx.event
    async def handle_submit(self, form_data: dict):
        if not await self._check_table_exists():
            yield rx.toast.error(
                "Operación bloqueada: No está conectado a la base de datos correcta (Novalink)."
            )
            return
        try:
            name = form_data.get("name", "").strip()
            description = form_data.get("description", "").strip()
            active = bool(form_data.get("active", False))
            if not name or not description:
                yield rx.toast.error("Usuario y Nombre Completo son requeridos.")
                return
            exclude_id = self.modal_user["id"] if self.is_editing else 0
            if await self.check_username_exists(name, exclude_id):
                yield rx.toast.error(f"El usuario '{name}' ya existe.")
                return
            if self.is_editing:
                query = """
                    UPDATE public.usuarios 
                    SET 
                        nombre = :name, 
                        descripcion = :description, 
                        activo = :active, 
                        usuariomodifica = 1,
                        fechamodificacion = NOW()
                    WHERE id = :id
                """
                await self._execute_write(
                    query,
                    {
                        "id": self.modal_user["id"],
                        "name": name,
                        "description": description,
                        "active": active,
                    },
                )
                yield rx.toast.success(f"Usuario '{name}' actualizado correctamente")
            else:
                next_id_result = await self._execute_query(
                    "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM public.usuarios"
                )
                next_id = next_id_result[0]["next_id"] if next_id_result else 1
                default_pwd_hash = hashlib.sha256("12345678".encode()).hexdigest()
                query = """
                    INSERT INTO public.usuarios 
                    (id, nombre, descripcion, perfil, pwd, cambiarpwd, caducapwd, activo, usuariocrea, fechacreacion)
                    VALUES 
                    (:id, :name, :description, 1, :pwd, false, false, :active, 1, NOW())
                """
                await self._execute_write(
                    query,
                    {
                        "id": next_id,
                        "name": name,
                        "description": description,
                        "pwd": default_pwd_hash,
                        "active": active,
                    },
                )
                yield rx.toast.success(
                    f"Usuario '{name}' creado con contraseña '12345678'"
                )
            self.close_modal()
            await self.load_users()
        except Exception as e:
            logging.exception(f"Error saving user: {e}")
            yield rx.toast.error(f"Error al guardar usuario: {str(e)}")

    @rx.event
    def confirm_delete_user(self, user: User):
        self.user_to_delete = user
        self.show_delete_confirm = True

    @rx.event
    def cancel_delete(self):
        self.show_delete_confirm = False
        self.user_to_delete = None

    @rx.event
    async def delete_user(self):
        if not await self._check_table_exists():
            self.cancel_delete()
            yield rx.toast.error(
                "Operación bloqueada: No está conectado a la base de datos correcta (Novalink)."
            )
            return
        if self.user_to_delete:
            try:
                query = """
                    UPDATE public.usuarios 
                    SET 
                        activo = false, 
                        usuariomodifica = 1, 
                        fechamodificacion = NOW()
                    WHERE id = :id
                """
                await self._execute_write(query, {"id": self.user_to_delete["id"]})
                yield rx.toast.info(
                    f"Usuario '{self.user_to_delete['name']}' desactivado"
                )
                await self.load_users()
            except Exception as e:
                logging.exception(f"Error deleting user: {e}")
                yield rx.toast.error(f"Error al eliminar usuario: {str(e)}")
        self.cancel_delete()