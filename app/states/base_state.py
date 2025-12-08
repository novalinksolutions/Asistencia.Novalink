import reflex as rx
from pydantic import BaseModel
from app.states.database_state import DatabaseState
import secrets
import logging
from sqlalchemy import text


class NavItem(BaseModel):
    name: str
    icon: str
    label: str = ""
    sub_items: list["NavItem"] = []


class BaseState(DatabaseState):
    auth_token: str = rx.Cookie(
        name="session_token", max_age=1800, same_site="lax", secure=True
    )
    sidebar_collapsed: bool = False
    active_page: str = ""
    current_company_name: str = ""
    current_database_name: str = "novalink"
    logged_user_id: int = 0
    logged_user_name: str = ""
    logged_user_description: str = ""
    expanded_modules: dict[str, bool] = {
        "Parametros": True,
        "Seguridad": False,
        "Equipos": False,
        "Catálogos": False,
        "Asistencias": False,
    }
    force_password_change_on_login: bool = False
    password_expired_message: str = ""
    navigation_menu: list[NavItem] = [
        NavItem(
            name="Parametros",
            icon="settings",
            sub_items=[
                NavItem(name="Parámetros Generales", icon="sliders-horizontal"),
                NavItem(name="Tipo de Justificaciones", icon="file-text"),
                NavItem(name="Definir Feriados", icon="calendar-days"),
            ],
        ),
        NavItem(
            name="Seguridad",
            icon="lock",
            sub_items=[
                NavItem(name="Usuarios", icon="users"),
                NavItem(name="Roles", icon="shield"),
            ],
        ),
        NavItem(
            name="Equipos",
            icon="monitor-smartphone",
            sub_items=[
                NavItem(name="Conectividad", icon="wifi"),
                NavItem(name="Transacciones", icon="arrow-left-right"),
            ],
        ),
        NavItem(
            name="Catálogos",
            icon="book-marked",
            sub_items=[
                NavItem(name="Entidades", icon="building-2"),
                NavItem(name="Empleados", icon="user-circle"),
            ],
        ),
        NavItem(name="Asistencias", icon="clipboard-check", sub_items=[]),
    ]

    @rx.event
    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed
        if self.sidebar_collapsed:
            for key in self.expanded_modules:
                self.expanded_modules[key] = False

    @rx.event
    async def set_active_page(self, page: str):
        self.active_page = page
        if page == "Parámetros Generales":
            from app.states.parametros_generales_state import ParametrosGeneralesState

            state = await self.get_state(ParametrosGeneralesState)
            await state.on_load()
        elif page == "Tipo de Justificaciones":
            from app.states.tipo_justificaciones_state import TipoJustificacionesState

            state = await self.get_state(TipoJustificacionesState)
            await state.on_load()
        elif page == "Definir Feriados":
            from app.states.definir_feriados_state import DefinirFeriadosState

            state = await self.get_state(DefinirFeriadosState)
            await state.on_load()
        elif page == "Usuarios":
            from app.states.usuarios_state import UsuariosState

            state = await self.get_state(UsuariosState)
            await state.on_load()
        elif page == "Roles":
            from app.states.roles_state import RolesState

            state = await self.get_state(RolesState)
            await state.on_load()
        elif page == "Entidades":
            from app.states.entidades_state import EntidadesState

            state = await self.get_state(EntidadesState)
            await state.on_load()
        elif page == "Empleados":
            pass
        elif page == "Conectividad":
            from app.states.conectividad_state import ConectividadState

            state = await self.get_state(ConectividadState)
            await state.on_load()
        elif page == "Transacciones":
            from app.states.transacciones_state import TransaccionesState

            state = await self.get_state(TransaccionesState)
            await state.on_load()

    @rx.event
    def toggle_module(self, module_name: str):
        is_currently_expanded = self.expanded_modules.get(module_name, False)
        for key in self.expanded_modules:
            self.expanded_modules[key] = False
        if not is_currently_expanded:
            self.expanded_modules[module_name] = True

    @rx.var
    def active_module_name(self) -> str:
        for module in self.navigation_menu:
            if any((sub.name == self.active_page for sub in module.sub_items)):
                return module.name
        return ""

    @rx.var
    def is_test_mode(self) -> bool:
        """Check if the current database is the test environment."""
        return self.current_database_name == "novalink"

    @rx.var
    def user_initials(self) -> str:
        """Generate initials for the avatar based on the user description."""
        target = self.logged_user_description.strip() or self.logged_user_name.strip()
        if not target:
            return "US"
        words = target.split()
        initials = "".join((word[0] for word in words if word))
        return initials[:2].upper()

    async def _ensure_session_table(self):
        """Ensure the sessions table exists in the central database."""
        try:
            query = """
                CREATE TABLE IF NOT EXISTS public.sesiones (
                    id SERIAL PRIMARY KEY,
                    token VARCHAR(255) UNIQUE NOT NULL,
                    usuario_id INTEGER NOT NULL,
                    database_name VARCHAR(50) NOT NULL,
                    fecha_inicio TIMESTAMP DEFAULT NOW(),
                    fecha_ultimo_acceso TIMESTAMP DEFAULT NOW(),
                    fecha_expiracion TIMESTAMP,
                    ip_address VARCHAR(50),
                    user_agent TEXT,
                    activa BOOLEAN DEFAULT true
                );
                CREATE INDEX IF NOT EXISTS idx_sesiones_token ON public.sesiones(token);
            """
            await self._execute_write(query, target_db="novalink")
        except Exception as e:
            logging.exception(f"Error creating sessions table: {e}")

    @rx.event
    async def create_session(
        self,
        user_id: int,
        database_name: str,
        ip_address: str = "",
        user_agent: str = "",
    ):
        """Create a new session for the user."""
        await self._ensure_session_table()
        try:
            token = secrets.token_urlsafe(32)
            self.auth_token = token
            insert_query = """
                INSERT INTO public.sesiones (
                    token, usuario_id, database_name, 
                    fecha_inicio, fecha_ultimo_acceso, fecha_expiracion, 
                    ip_address, user_agent, activa
                ) VALUES (
                    :token, :uid, :db_name, 
                    NOW(), NOW(), NOW() + INTERVAL '30 minutes', 
                    :ip, :ua, true
                )
            """
            params = {
                "token": token,
                "uid": user_id,
                "db_name": database_name,
                "ip": ip_address,
                "ua": user_agent,
            }
            await self._execute_write(insert_query, params, target_db="novalink")
            logging.info(f"Session created for user {user_id} in {database_name}")
        except Exception as e:
            logging.exception(f"Error creating session: {e}")
            raise e

    @rx.event
    async def cleanup_expired_sessions(self):
        """Mark expired sessions as inactive."""
        try:
            query = """
                UPDATE public.sesiones 
                SET activa = false 
                WHERE fecha_expiracion < NOW() AND activa = true
            """
            await self._execute_write(query, target_db="novalink")
        except Exception as e:
            logging.exception(f"Error cleaning expired sessions: {e}")

    @rx.event
    async def validate_session(self) -> bool:
        """Validate the current session token."""
        await self._ensure_session_table()
        await self.cleanup_expired_sessions()
        if not self.auth_token:
            return False
        try:
            query = """
                SELECT 
                    id, usuario_id, database_name, fecha_expiracion, activa
                FROM public.sesiones 
                WHERE token = :token
            """
            results = await self._execute_query(
                query, {"token": self.auth_token}, target_db="novalink"
            )
            if not results:
                return False
            session = results[0]
            if not session["activa"]:
                return False
            check_exp_query = """
                SELECT 1 FROM public.sesiones 
                WHERE token = :token AND fecha_expiracion > NOW()
            """
            valid_results = await self._execute_query(
                check_exp_query, {"token": self.auth_token}, target_db="novalink"
            )
            if not valid_results:
                await self.close_session()
                return False
            update_query = """
                UPDATE public.sesiones 
                SET 
                    fecha_ultimo_acceso = NOW(),
                    fecha_expiracion = NOW() + INTERVAL '30 minutes'
                WHERE token = :token
            """
            await self._execute_write(
                update_query, {"token": self.auth_token}, target_db="novalink"
            )
            logging.info(
                f"Session renewed for user {session['usuario_id']} via validation"
            )
            self.logged_user_id = session["usuario_id"]
            self.current_database_name = session["database_name"]
            if not self.logged_user_name:
                try:
                    user_query = "SELECT nombre, descripcion FROM public.usuarios WHERE id = :uid"
                    user_res = await self._execute_query(
                        user_query,
                        {"uid": session["usuario_id"]},
                        target_db=session["database_name"],
                    )
                    if user_res:
                        self.logged_user_name = user_res[0]["nombre"]
                        self.logged_user_description = user_res[0]["descripcion"] or ""
                except Exception as e:
                    logging.exception(f"Could not re-hydrate user details: {e}")
            return True
        except Exception as e:
            logging.exception(f"Session validation error: {e}")
            return False

    @rx.event
    async def close_session(self):
        """Close the current session."""
        await self._ensure_session_table()
        if self.auth_token:
            try:
                query = "UPDATE public.sesiones SET activa = false WHERE token = :token"
                await self._execute_write(
                    query, {"token": self.auth_token}, target_db="novalink"
                )
                logging.info("Session explicitly closed via logout")
            except Exception as e:
                logging.exception(f"Error closing session: {e}")
        self.auth_token = ""

    @rx.event
    async def update_catalog_labels(self):
        """Update catalog menu items labels based on parameters."""
        if not self.has_db_connection:
            return
        try:
            query = "SELECT codigo, valor FROM public.parametros WHERE codigo IN (5, 8, 11, 14, 17)"
            results = await self._execute_query(query, target_db="novalink")
            params = {row["codigo"]: row["valor"] for row in results}
            for module in self.navigation_menu:
                if module.name == "Catálogos":
                    for sub in module.sub_items:
                        if sub.name == "Nivel 1":
                            sub.label = params.get(5, "Nivel 1")
                        elif sub.name == "Nivel 2":
                            sub.label = params.get(8, "Nivel 2")
                        elif sub.name == "Nivel 3":
                            sub.label = params.get(11, "Nivel 3")
                        elif sub.name == "Nivel 4":
                            sub.label = params.get(14, "Nivel 4")
                        elif sub.name == "Nivel 5":
                            sub.label = params.get(17, "Nivel 5")
                    break
            self.navigation_menu = list(self.navigation_menu)
        except Exception as e:
            logging.exception(f"Error updating catalog labels: {e}")

    @rx.event
    async def check_login(self):
        """Validate session on page load. Redirect to login if invalid."""
        is_valid = await self.validate_session()
        if not is_valid:
            logging.warning(
                "Invalid or expired session detected during check_login. Redirecting to login."
            )
            return rx.redirect("/login")
        await self.update_catalog_labels()