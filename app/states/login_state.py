import reflex as rx
import asyncio
import logging
import hashlib
from typing import TypedDict
from app.states.database_state import DatabaseState


class Company(TypedDict):
    id: str
    name: str
    db_name: str


class LoginState(DatabaseState):
    companies: list[Company] = []
    empresa: str = ""
    username: str = ""
    password: str = ""
    error_message: str = ""
    is_loading: bool = False
    search_text: str = ""
    show_suggestions: bool = False
    password_expired: bool = False
    password_validity_days: int = 0

    @rx.var
    def filtered_companies(self) -> list[Company]:
        if len(self.search_text) < 3:
            return []
        search = self.search_text.lower()
        return [c for c in self.companies if search in c["name"].lower()]

    @rx.var
    def is_test_company_selected(self) -> bool:
        """Check if the selected company is the test environment."""
        return self.empresa == "novalink_test"

    @rx.event
    async def on_load(self):
        """Load initial data when the login page loads and clean state."""
        self.error_message = ""
        self.search_text = ""
        self.show_suggestions = False
        self.username = ""
        self.password = ""
        self.empresa = ""
        self.is_loading = False
        await self.load_companies()

    @rx.event
    def set_search_text_change(self, value: str):
        """Update search text and toggle suggestions visibility."""
        self.search_text = value
        if len(value) >= 3:
            self.show_suggestions = True
        else:
            self.show_suggestions = False
            if value == "":
                self.empresa = ""

    @rx.event
    def select_company(self, company_id: str, company_name: str):
        """Select a company from the suggestions list."""
        self.empresa = company_id
        self.search_text = company_name
        self.show_suggestions = False

    @rx.event
    def clear_company_selection(self):
        """Clear the selected company to allow searching again."""
        self.empresa = ""
        self.search_text = ""
        self.show_suggestions = False

    @rx.event
    async def load_companies(self):
        """Load available companies from the database."""
        test_company = {
            "id": "novalink_test",
            "name": "Corporación Novalink",
            "db_name": "novalink",
        }
        try:
            query = "SELECT id, nombre, COALESCE(base, 'serviciosdev') as db_name FROM cliente.catalogo WHERE activo = true ORDER BY nombre"
            results = await self._execute_query(query, target_db="serviciosdev")
            db_companies = [
                {
                    "id": str(row["id"]),
                    "name": str(row["nombre"]),
                    "db_name": str(row["db_name"]),
                }
                for row in results
            ]
            self.companies = [test_company] + db_companies
        except Exception as e:
            logging.exception(f"Error loading companies: {e}")
            self.companies = [
                test_company,
                {
                    "id": "1",
                    "name": "Empresa Demo (Offline)",
                    "db_name": "serviciosdev",
                },
            ]

    @rx.event
    async def handle_login(self, form_data: dict):
        """Handle the login form submission."""
        self.is_loading = True
        self.error_message = ""
        yield
        await asyncio.sleep(1)
        self.empresa = (form_data.get("empresa") or "").strip()
        self.username = (form_data.get("username") or "").strip()
        self.password = (form_data.get("password") or "").strip()
        if not self.empresa or not self.username or (not self.password):
            if not self.empresa and self.search_text:
                self.error_message = "Debe seleccionar una empresa válida de la lista."
            else:
                self.error_message = "Todos los campos son obligatorios."
            self.is_loading = False
            yield rx.toast.error(self.error_message)
            return
        selected_company = next(
            (c for c in self.companies if c["id"] == self.empresa), None
        )
        if not selected_company:
            self.error_message = "Empresa seleccionada no válida."
            self.is_loading = False
            yield rx.toast.error(self.error_message)
            return
        target_db = selected_company["db_name"]
        if not self.verify_connection(target_db):
            self.error_message = f"Error de conexión con la base de datos: {target_db}"
            self.is_loading = False
            yield rx.toast.error(self.error_message)
            return
        try:
            query = """
                SELECT id, nombre, descripcion, pwd, activo 
                FROM public.usuarios 
                WHERE nombre = :username
            """
            results = await self._execute_query(
                query, {"username": self.username}, target_db=target_db
            )
            if not results:
                self.error_message = "Usuario no encontrado."
                self.is_loading = False
                yield rx.toast.error(self.error_message)
                return
            user = results[0]
            stored_hash = user.get("pwd", "")
            is_active = bool(user.get("activo", False))
            input_hash = hashlib.sha256(self.password.encode()).hexdigest()
            if input_hash != stored_hash:
                self.error_message = "Contraseña incorrecta."
                self.is_loading = False
                yield rx.toast.error(self.error_message)
                return
            if not is_active:
                self.error_message = "El usuario se encuentra inactivo."
                self.is_loading = False
                yield rx.toast.error(self.error_message)
                return
            validity_days = 90
            try:
                param_query = "SELECT valor FROM parametros WHERE codigo = 80"
                param_result = await self._execute_query(
                    param_query, target_db=target_db
                )
                if param_result:
                    validity_days = int(param_result[0]["valor"])
            except Exception as e:
                logging.exception(f"Could not fetch password validity parameter: {e}")
            check_query = """
                SELECT 
                    CASE 
                        WHEN fechacambiopwd IS NULL THEN 1 
                        WHEN EXTRACT(DAY FROM NOW() - fechacambiopwd) > :days THEN 1 
                        ELSE 0 
                    END as is_expired
                FROM usuarios 
                WHERE id = :uid
            """
            expiration_result = await self._execute_query(
                check_query,
                {"uid": user["id"], "days": validity_days},
                target_db=target_db,
            )
            is_expired = False
            if expiration_result and expiration_result[0]["is_expired"] == 1:
                is_expired = True
            from app.states.base_state import BaseState

            base_state = await self.get_state(BaseState)
            base_state.current_company_name = selected_company["name"]
            base_state.current_database_name = target_db
            base_state.logged_user_id = user["id"]
            base_state.logged_user_name = user["nombre"]
            base_state.logged_user_description = (
                user.get("descripcion") or user["nombre"]
            )
            if is_expired:
                base_state.force_password_change_on_login = True
                base_state.password_expired_message = (
                    "Su contraseña ha expirado. Por favor cámbiela para continuar."
                )
                logging.info(
                    f"User {self.username} login successful but password expired."
                )
            else:
                base_state.force_password_change_on_login = False
                base_state.password_expired_message = ""
                logging.info(
                    f"User {self.username} logged in successfully. Connected to DB: {target_db}"
                )
            headers = self.router.headers
            ip_address = "unknown"
            user_agent = "unknown"
            try:
                try:
                    ip_address = headers.raw_headers.get("x-forwarded-for")
                    if not ip_address:
                        ip_address = headers.host
                except Exception as e:
                    logging.exception(f"Error accessing x-forwarded-for header: {e}")
                    try:
                        ip_address = headers.host
                    except Exception as e2:
                        logging.exception(f"Error accessing host header: {e2}")
                try:
                    user_agent = headers.user_agent
                except Exception as e:
                    logging.exception(f"Error accessing user-agent header: {e}")
            except Exception as e:
                logging.exception(f"Error reading headers for session tracking: {e}")
            logging.info(
                f"Creating session for user {user['nombre']} (ID: {user['id']}) IP: {ip_address}"
            )
            await base_state.create_session(
                user_id=user["id"],
                database_name=target_db,
                ip_address=str(ip_address),
                user_agent=str(user_agent),
            )
            self.is_loading = False
            yield rx.toast.success(
                f"¡Bienvenido {user['nombre']}! Conectado a {selected_company['name']}"
            )
            yield rx.redirect("/dashboard")
        except Exception as e:
            logging.exception(f"Login error: {e}")
            self.error_message = f"Error durante el inicio de sesión: {str(e)}"
            self.is_loading = False
            yield rx.toast.error(self.error_message)