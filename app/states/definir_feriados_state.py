import reflex as rx
from typing import TypedDict, Literal
import datetime
import calendar
import logging
from sqlalchemy import text
from app.states.database_state import DatabaseState

HolidayType = Literal[
    "descanso_obligatorio", "feriado_recuperable", "jornada_recuperacion"
]


class Day(TypedDict):
    day_num: int
    date_str: str
    is_current_month: bool


class Month(TypedDict):
    month_name: str
    weeks: list[list[Day]]


class AdministrativeLevel(TypedDict):
    id: str
    name: str


class DefinirFeriadosState(DatabaseState):
    selected_year: int = datetime.date.today().year
    holidays: dict[str, HolidayType] = {}
    readonly_holidays: dict[str, HolidayType] = {}
    show_nivel_filter: bool = False
    nivel_asociacion_numero: int = 0
    niveles_administrativos: list[AdministrativeLevel] = []
    nivel_administrativo_seleccionado: str = ""
    spanish_months: dict[str, str] = {
        "January": "Enero",
        "February": "Febrero",
        "March": "Marzo",
        "April": "Abril",
        "May": "Mayo",
        "June": "Junio",
        "July": "Julio",
        "August": "Agosto",
        "September": "Septiembre",
        "October": "Octubre",
        "November": "Noviembre",
        "December": "Diciembre",
    }

    @rx.event
    async def on_load(self):
        """Load holidays from database on page load."""
        await self.check_configuration()
        await self.load_holidays_from_db()

    @rx.event
    async def check_configuration(self):
        """Check configuration for administrative levels."""
        if not self.has_db_connection:
            self.show_nivel_filter = False
            return
        try:
            query = (
                "SELECT codigo, valor FROM public.parametros WHERE codigo IN (20, 21)"
            )
            results = await self._execute_query(query, target_db="novalink")
            params = {row["codigo"]: row["valor"] for row in results}
            is_enabled = params.get(20, "0") == "1"
            if is_enabled:
                self.show_nivel_filter = True
                self.nivel_asociacion_numero = int(params.get(21, "4"))
                if self.nivel_asociacion_numero not in [1, 2, 3, 4, 5]:
                    logging.error(
                        f"Invalid association level number: {self.nivel_asociacion_numero}"
                    )
                    self.show_nivel_filter = False
                    return
                table_name = f"public.niveladm{self.nivel_asociacion_numero}"
                level_query = f"SELECT codigo::text as id, descripcion as name FROM {table_name} WHERE codigo > 0 ORDER BY descripcion"
                level_results = await self._execute_query(
                    level_query, target_db="novalink"
                )
                self.niveles_administrativos = [
                    AdministrativeLevel(id=row["id"], name=row["name"])
                    for row in level_results
                ]
                self.niveles_administrativos.insert(
                    0, AdministrativeLevel(id="-1", name="< TODOS >")
                )
                if self.niveles_administrativos and (
                    not self.nivel_administrativo_seleccionado
                ):
                    self.nivel_administrativo_seleccionado = (
                        self.niveles_administrativos[0]["id"]
                    )
            else:
                self.show_nivel_filter = False
                self.nivel_asociacion_numero = 0
                self.niveles_administrativos = []
                self.nivel_administrativo_seleccionado = ""
        except Exception as e:
            logging.exception(f"Error checking configuration: {e}")
            self.show_nivel_filter = False

    @rx.event
    async def set_nivel_administrativo_seleccionado(self, value: str):
        self.nivel_administrativo_seleccionado = value
        await self.load_holidays_from_db()

    @rx.event
    async def load_holidays_from_db(self):
        """Load holidays for the selected year from database."""
        from app.states.base_state import BaseState

        base_state = await self.get_state(BaseState)
        self.holidays = {}
        self.readonly_holidays = {}
        if (
            not self.has_db_connection
            or base_state.current_database_name == "serviciosdev"
        ):
            self.holidays = {
                f"{self.selected_year}-01-01": "descanso_obligatorio",
                f"{self.selected_year}-05-01": "descanso_obligatorio",
                f"{self.selected_year}-07-20": "descanso_obligatorio",
                f"{self.selected_year}-08-07": "descanso_obligatorio",
                f"{self.selected_year}-12-08": "descanso_obligatorio",
                f"{self.selected_year}-12-25": "descanso_obligatorio",
                f"{self.selected_year}-04-17": "feriado_recuperable",
                f"{self.selected_year}-04-18": "feriado_recuperable",
            }
            if (
                self.show_nivel_filter
                and self.nivel_administrativo_seleccionado
                and (self.nivel_administrativo_seleccionado != "-1")
            ):
                self.readonly_holidays = {
                    f"{self.selected_year}-01-01": "descanso_obligatorio",
                    f"{self.selected_year}-12-25": "descanso_obligatorio",
                }
                del self.holidays[f"{self.selected_year}-01-01"]
                del self.holidays[f"{self.selected_year}-12-25"]
            return
        try:
            type_mapping = {
                1: "descanso_obligatorio",
                2: "feriado_recuperable",
                3: "jornada_recuperacion",
            }
            if (
                self.show_nivel_filter
                and self.nivel_administrativo_seleccionado
                and (self.nivel_administrativo_seleccionado != "-1")
            ):
                query_editable = "SELECT fecha::text as fecha, tipo FROM feriados WHERE anio = :year AND codigoniveladm = :cod_nivel"
                params_editable = {
                    "year": self.selected_year,
                    "cod_nivel": int(self.nivel_administrativo_seleccionado),
                }
                results_editable = await self._execute_query(
                    query_editable, params_editable
                )
                self.holidays = {
                    row["fecha"]: type_mapping.get(row["tipo"])
                    for row in results_editable
                    if row["tipo"] in type_mapping
                }
                query_readonly = "SELECT fecha::text as fecha, tipo FROM feriados WHERE anio = :year AND codigoniveladm = -1"
                params_readonly = {"year": self.selected_year}
                results_readonly = await self._execute_query(
                    query_readonly, params_readonly
                )
                self.readonly_holidays = {
                    row["fecha"]: type_mapping.get(row["tipo"])
                    for row in results_readonly
                    if row["tipo"] in type_mapping
                }
            else:
                query = "SELECT fecha::text as fecha, tipo FROM feriados WHERE anio = :year AND codigoniveladm = -1"
                params = {"year": self.selected_year}
                results = await self._execute_query(query, params)
                self.holidays = {
                    row["fecha"]: type_mapping.get(row["tipo"])
                    for row in results
                    if row["tipo"] in type_mapping
                }
        except Exception as e:
            logging.exception(f"Error loading holidays: {e}")
            self.holidays = {
                f"{self.selected_year}-01-01": "descanso_obligatorio",
                f"{self.selected_year}-05-01": "descanso_obligatorio",
                f"{self.selected_year}-12-25": "descanso_obligatorio",
            }

    @rx.event
    async def increment_year(self):
        self.selected_year += 1
        await self.load_holidays_from_db()

    @rx.event
    async def decrement_year(self):
        self.selected_year -= 1
        await self.load_holidays_from_db()

    @rx.event
    def toggle_holiday(self, date_str: str):
        if date_str in self.readonly_holidays:
            return
        current_type = self.holidays.get(date_str)
        if current_type is None:
            self.holidays[date_str] = "descanso_obligatorio"
        elif current_type == "descanso_obligatorio":
            self.holidays[date_str] = "feriado_recuperable"
        elif current_type == "feriado_recuperable":
            self.holidays[date_str] = "jornada_recuperacion"
        else:
            del self.holidays[date_str]

    @rx.event
    async def save_holidays(self):
        if not self.has_db_connection:
            return rx.toast.success(
                f"Simulación: Feriados {self.selected_year} guardados"
            )
        try:
            from app.states.base_state import BaseState

            base_state = await self.get_state(BaseState)
            user = base_state.logged_user_name or "system"
            engine = self._get_db_engine(base_state.current_database_name or "novalink")
            if not engine:
                return rx.toast.error("No hay conexión a la base de datos")
            params_query = (
                "SELECT codigo, valor FROM public.parametros WHERE codigo IN (4, 20)"
            )
            params_result = await self._execute_query(
                params_query, target_db="novalink"
            )
            params_map = {row["codigo"]: row["valor"] for row in params_result}
            param_4 = int(params_map.get(4, "4"))
            param_20 = params_map.get(20, "0")
            nivelasociacion = 0
            codigoniveladm = -1
            if param_20 == "0":
                nivelasociacion = 0
                codigoniveladm = -1
            else:
                nivelasociacion = param_4
                if (
                    self.nivel_administrativo_seleccionado == "-1"
                    or not self.nivel_administrativo_seleccionado
                ):
                    codigoniveladm = -1
                else:
                    codigoniveladm = int(self.nivel_administrativo_seleccionado)
            type_mapping_rev = {
                "descanso_obligatorio": 1,
                "feriado_recuperable": 2,
                "jornada_recuperacion": 3,
            }
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "DELETE FROM feriados WHERE anio = :year AND codigoniveladm = :cod_nivel"
                    ),
                    {"year": self.selected_year, "cod_nivel": codigoniveladm},
                )
                for date_str, type_str in self.holidays.items():
                    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    if dt.year == self.selected_year:
                        tipo_val = type_mapping_rev.get(type_str, 1)
                        insert_query = """
                            INSERT INTO feriados (
                                fecha, anio, mes, dia, fila, 
                                nivelasociacion, codigoniveladm, 
                                usuario, fechahoraauditoria, tipo, horas
                            ) VALUES (
                                :fecha, :anio, :mes, :dia, 1,
                                :nivel_asoc, :cod_nivel,
                                :usuario, NOW(), :tipo, 0
                            )
                        """
                        conn.execute(
                            text(insert_query),
                            {
                                "fecha": date_str,
                                "anio": dt.year,
                                "mes": dt.month,
                                "dia": dt.day,
                                "usuario": user,
                                "tipo": tipo_val,
                                "nivel_asoc": nivelasociacion,
                                "cod_nivel": codigoniveladm,
                            },
                        )
            return rx.toast.success(
                f"Feriados del año {self.selected_year} guardados correctamente."
            )
        except Exception as e:
            logging.exception(f"Error saving holidays: {e}")
            return rx.toast.error("Error al guardar los feriados.")

    @rx.event
    async def load_holidays(self):
        await self.load_holidays_from_db()
        return rx.toast.info(
            f"Feriados del año {self.selected_year} cargados desde la base de datos"
        )

    @rx.var
    def calendar_data(self) -> list[Month]:
        year = self.selected_year
        months_data = []
        cal = calendar.Calendar(firstweekday=6)
        for month_num in range(1, 13):
            month_name_en = datetime.date(year, month_num, 1).strftime("%B")
            month_name_es = self.spanish_months.get(month_name_en, month_name_en)
            month_calendar = cal.monthdatescalendar(year, month_num)
            weeks_data = []
            for week in month_calendar:
                week_days = []
                for day_date in week:
                    week_days.append(
                        {
                            "day_num": day_date.day,
                            "date_str": day_date.strftime("%Y-%m-%d"),
                            "is_current_month": day_date.month == month_num,
                        }
                    )
                weeks_data.append(week_days)
            months_data.append({"month_name": month_name_es, "weeks": weeks_data})
        return months_data