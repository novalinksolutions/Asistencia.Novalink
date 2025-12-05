import reflex as rx
from typing import TypedDict
import logging
from sqlalchemy import text
from app.states.database_state import DatabaseState


class Permission(TypedDict):
    id: str
    name: str


class Role(TypedDict):
    id: str
    name: str
    description: str
    permissions: list[str]


class RolesState(DatabaseState):
    all_permissions: list[Permission] = []
    roles: list[Role] = []
    show_modal: bool = False
    is_editing: bool = False
    modal_role: Role = {"id": "0", "name": "", "description": "", "permissions": []}
    show_delete_confirm: bool = False
    role_to_delete: Role | None = None

    @rx.event
    async def on_load(self):
        """Load roles and permissions from database on page load."""
        await self.load_permissions()
        await self.load_roles()

    @rx.event
    async def load_permissions(self):
        """Load modules as permissions from 'modulos' table."""
        try:
            query = """
                SELECT 
                    id::text,
                    descripcion as name
                FROM modulos 
                ORDER BY descripcion ASC
            """
            results = await self._execute_query(query)
            if results:
                self.all_permissions = [
                    Permission(id=row["id"], name=row["name"]) for row in results
                ]
            else:
                self.all_permissions = []
        except Exception as e:
            logging.exception(f"Error loading permissions (modules): {e}")
            self.all_permissions = []

    @rx.event
    async def load_roles(self):
        """Load profiles from 'perfiles' table."""
        try:
            roles_query = """
                SELECT 
                    id::text,
                    descripcion as name
                FROM perfiles 
                WHERE activo = true 
                ORDER BY descripcion ASC
            """
            roles_results = await self._execute_query(roles_query)
            permissions_query = """
                SELECT 
                    perfil::text as role_id,
                    modulo::text as permission_id
                FROM modulosperfil
            """
            permissions_results = await self._execute_query(permissions_query)
            role_permissions = {}
            for perm in permissions_results:
                role_id = perm["role_id"]
                if role_id not in role_permissions:
                    role_permissions[role_id] = []
                role_permissions[role_id].append(perm["permission_id"])
            self.roles = [
                Role(
                    id=row["id"],
                    name=row["name"],
                    description="",
                    permissions=role_permissions.get(row["id"], []),
                )
                for row in roles_results
            ]
        except Exception as e:
            logging.exception(f"Error loading roles (perfiles): {e}")
            self.roles = []

    def _get_empty_role(self) -> Role:
        return {"id": "0", "name": "", "description": "", "permissions": []}

    @rx.event
    def open_add_modal(self):
        self.is_editing = False
        self.modal_role = self._get_empty_role()
        self.show_modal = True

    @rx.event
    def open_edit_modal(self, role: Role):
        self.is_editing = True
        self.modal_role = role
        self.show_modal = True

    @rx.event
    def close_modal(self):
        self.show_modal = False

    @rx.event
    async def handle_submit(self, form_data: dict):
        name = form_data.get("name", "").strip()
        description = form_data.get("description", "").strip()
        if not name:
            return rx.toast.error("El nombre del rol es requerido.")
        from app.states.base_state import BaseState

        base_state = await self.get_state(BaseState)
        user_id = base_state.logged_user_id or 1
        current_db = base_state.current_database_name or "novalink"
        engine = self._get_db_engine(current_db)
        if not engine:
            return rx.toast.error("Error de conexión a la base de datos")
        try:
            with engine.begin() as conn:
                role_id = 0
                if self.is_editing and self.modal_role["id"] != "0":
                    role_id = int(self.modal_role["id"])
                    conn.execute(
                        text("""
                            UPDATE perfiles 
                            SET descripcion = :name, usuariomodifica = :uid, fechamodificacion = NOW() 
                            WHERE id = :id
                        """),
                        {"name": name, "uid": user_id, "id": role_id},
                    )
                else:
                    result = conn.execute(
                        text("""
                            INSERT INTO perfiles (descripcion, activo, usuariocrea, fechacreacion) 
                            VALUES (:name, true, :uid, NOW()) 
                            RETURNING id
                        """),
                        {"name": name, "uid": user_id},
                    )
                    role_id = result.scalar()
                conn.execute(
                    text("DELETE FROM modulosperfil WHERE perfil = :id"),
                    {"id": role_id},
                )
                if self.modal_role["permissions"]:
                    for mod_id in self.modal_role["permissions"]:
                        conn.execute(
                            text("""
                                INSERT INTO modulosperfil (perfil, modulo, usuariocrea, fechacreacion) 
                                VALUES (:id, :mod, :uid, NOW())
                            """),
                            {"id": role_id, "mod": int(mod_id), "uid": user_id},
                        )
            action = "actualizado" if self.is_editing else "creado"
            self.close_modal()
            await self.load_roles()
            return rx.toast.success(f"Rol '{name}' {action} correctamente.")
        except Exception as e:
            logging.exception(f"Error saving role: {e}")
            return rx.toast.error(f"Error al guardar: {e}")

    @rx.event
    def toggle_permission(self, perm_id: str):
        if perm_id in self.modal_role["permissions"]:
            self.modal_role["permissions"].remove(perm_id)
        else:
            self.modal_role["permissions"].append(perm_id)

    @rx.event
    def confirm_delete_role(self, role: Role):
        self.role_to_delete = role
        self.show_delete_confirm = True

    @rx.event
    def cancel_delete(self):
        self.show_delete_confirm = False
        self.role_to_delete = None

    @rx.event
    async def delete_role(self):
        if self.role_to_delete:
            from app.states.base_state import BaseState

            base_state = await self.get_state(BaseState)
            user_id = base_state.logged_user_id or 1
            try:
                query = """
                    UPDATE perfiles 
                    SET activo = false, usuariomodifica = :uid, fechamodificacion = NOW() 
                    WHERE id = :id
                """
                await self._execute_write(
                    query, {"id": int(self.role_to_delete["id"]), "uid": user_id}
                )
                rx.toast.info(f"Rol '{self.role_to_delete['name']}' eliminado.")
                await self.load_roles()
            except Exception as e:
                logging.exception(f"Error deleting role: {e}")
                rx.toast.error("Error al eliminar el rol.")
        self.cancel_delete()