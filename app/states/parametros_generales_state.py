import reflex as rx
import asyncio
import logging
from app.states.database_state import DatabaseState
from sqlalchemy import text


class ParametrosGeneralesState(DatabaseState):
    niveles_habilitados: int = 4
    nivel_1: str = ""
    nivel_2: str = ""
    nivel_3: str = ""
    nivel_4: str = ""
    nivel_5: str = ""
    asociar_calendario: bool = False
    nivel_asociacion: str = "4"
    param_35: str = "0"
    param_36: str = ""
    param_39: str = "0"
    param_40: str = ""
    is_loading: bool = False
    association_levels: list[str] = ["1", "2", "3", "4", "5"]

    @rx.event
    async def on_load(self):
        """Load parameters from database on page load."""
        logging.info("🔄 Mounting Parámetros Generales page and loading data...")
        await self.load_parameters()

    @rx.event
    async def load_parameters(self):
        """Load administrative levels from public.parametros using correct codes."""
        if not self.has_db_connection:
            self.niveles_habilitados = 4
            self.nivel_1 = "Institución"
            self.nivel_2 = "Lideres"
            self.nivel_3 = "Modelo"
            self.nivel_4 = "Feriados"
            self.nivel_5 = "< No definido >"
            self.asociar_calendario = True
            self.nivel_asociacion = "4"
            self.param_35 = "0"
            self.param_36 = "Valor Numérico"
            self.param_39 = "0"
            self.param_40 = "Descripción de prueba"
            return
        try:
            query = """
                SELECT codigo, valor
                FROM public.parametros 
                WHERE codigo IN (4, 5, 8, 11, 14, 17, 20, 21, 35, 36, 39, 40)
            """
            results = await self._execute_query(query, target_db="novalink")
            params = {row["codigo"]: row["valor"] for row in results}
            self.niveles_habilitados = int(params.get(4, "4"))
            self.nivel_1 = params.get(5, "")
            self.nivel_2 = params.get(8, "")
            self.nivel_3 = params.get(11, "")
            self.nivel_4 = params.get(14, "")
            self.nivel_5 = params.get(17, "")
            self.asociar_calendario = params.get(20, "0") == "1"
            self.nivel_asociacion = params.get(21, "4")
            self.param_35 = params.get(35, "0")
            self.param_36 = params.get(36, "")
            self.param_39 = params.get(39, "0")
            self.param_40 = params.get(40, "")
        except Exception as e:
            logging.exception(f"Error loading parameters: {e}")
            rx.toast.error("Error al cargar parámetros de la base de datos")

    def _update_param(self, conn, codigo: int, valor: str | int):
        """Helper to update a single parameter."""
        val_str = str(valor)
        logging.info(f"Executing UPDATE: code={codigo}, value='{val_str}'")
        conn.execute(
            text("UPDATE public.parametros SET valor = :valor WHERE codigo = :codigo"),
            {"valor": val_str, "codigo": codigo},
        )

    @rx.event
    async def save_parameters(self):
        """Save current state to database using correct codes."""
        self.is_loading = True
        yield
        if not self.has_db_connection:
            await asyncio.sleep(1)
            self.is_loading = False
            yield rx.toast.success("Simulación: Parámetros guardados localmente")
            return
        try:
            engine = self._get_db_engine("novalink")
            if not engine:
                raise Exception("No connection to novalink database")
            logging.info(
                f"Starting save_parameters transaction. Niveles habilitados: {self.niveles_habilitados}"
            )
            with engine.begin() as conn:
                self._update_param(conn, 4, self.niveles_habilitados)
                self._update_param(conn, 5, self.nivel_1)
                self._update_param(conn, 8, self.nivel_2)
                self._update_param(conn, 11, self.nivel_3)
                self._update_param(conn, 14, self.nivel_4)
                self._update_param(conn, 17, self.nivel_5)
                self._update_param(conn, 20, "1" if self.asociar_calendario else "0")
                self._update_param(conn, 21, self.nivel_asociacion)
                self._update_param(conn, 35, self.param_35)
                self._update_param(conn, 36, self.param_36)
                self._update_param(conn, 39, self.param_39)
                self._update_param(conn, 40, self.param_40)
            logging.info("Transaction committed successfully.")
            self.is_loading = False
            yield rx.toast.success("Parámetros actualizados correctamente en Novalink")
            await self.load_parameters()
        except Exception as e:
            logging.exception(f"Error saving parameters: {e}")
            self.is_loading = False
            yield rx.toast.error(f"Error al guardar cambios: {str(e)}")

    @rx.event
    def set_niveles_habilitados(self, value: str | int):
        try:
            self.niveles_habilitados = int(value)
        except (ValueError, TypeError) as e:
            logging.exception(f"Error setting niveles habilitados: {e}")

    @rx.event
    def set_nivel_1(self, value: str):
        self.nivel_1 = value

    @rx.event
    def set_nivel_2(self, value: str):
        self.nivel_2 = value

    @rx.event
    def set_nivel_3(self, value: str):
        self.nivel_3 = value

    @rx.event
    def set_nivel_4(self, value: str):
        self.nivel_4 = value

    @rx.event
    def set_nivel_5(self, value: str):
        self.nivel_5 = value

    @rx.event
    def set_asociar_calendario(self, checked: bool):
        self.asociar_calendario = checked

    @rx.event
    def set_nivel_asociacion(self, value: str):
        self.nivel_asociacion = value

    @rx.event
    def set_param_35(self, checked: bool):
        self.param_35 = "1" if checked else "0"

    @rx.event
    def set_param_36(self, value: str):
        self.param_36 = value

    @rx.event
    def set_param_39(self, checked: bool):
        self.param_39 = "1" if checked else "0"

    @rx.event
    def set_param_40(self, value: str):
        self.param_40 = value