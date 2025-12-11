import reflex as rx
from typing import Optional, TypedDict
from app.states.database_state import DatabaseState
import logging


class Dispositivo(TypedDict):
    id: int
    codigo: str
    descripcion: str
    activo: bool
    en_linea: bool


class ConectividadState(DatabaseState):
    """State for managing device connectivity."""

    dispositivos: list[Dispositivo] = []
    search_query: str = ""
    is_loading: bool = False
    show_dialog: bool = False
    current_dispositivo: dict = {}
    error_message: str = ""

    @rx.event
    async def on_load(self):
        """Load connectivity data on page load."""
        logging.info("🔄 Loading Conectividad page...")
        await self.load_dispositivos()

    @rx.event
    async def load_dispositivos(self):
        """Fetch all devices from the database."""
        self.is_loading = True
        try:
            query = "SELECT codigo, descripcion, activo, enlinea FROM public.dispositivos ORDER BY codigo"
            results = await self._execute_query(query, target_db="novalink")
            self.dispositivos = [
                Dispositivo(
                    id=int(row["codigo"]),
                    codigo=str(row["codigo"]),
                    descripcion=row["descripcion"] or "",
                    activo=bool(row["activo"]),
                    en_linea=bool(row["enlinea"]),
                )
                for row in results
            ]
        except Exception as e:
            logging.exception(f"Error loading dispositivos: {e}")
            self.error_message = "Error al cargar dispositivos."
        finally:
            self.is_loading = False

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

    @rx.event
    def open_dialog(self, dispositivo: Optional[dict] = None):
        """Open the create/edit dialog."""
        if dispositivo:
            self.current_dispositivo = dispositivo.copy()
        else:
            self.current_dispositivo = {
                "id": 0,
                "codigo": "",
                "descripcion": "",
                "activo": True,
                "en_linea": False,
            }
        self.show_dialog = True
        self.error_message = ""

    @rx.event
    def close_dialog(self):
        self.show_dialog = False

    @rx.event
    def update_current_field(self, field: str, value: str | bool):
        """Update a field in the current device being edited."""
        self.current_dispositivo[field] = value

    @rx.event
    async def save_dispositivo(self):
        """Save or update the device."""
        code_str = str(self.current_dispositivo.get("codigo", "")).strip()
        desc = self.current_dispositivo.get("descripcion", "").strip()
        if not code_str or not desc:
            self.error_message = "Código y descripción son obligatorios."
            return
        try:
            code = int(code_str)
        except ValueError as e:
            logging.exception(f"Error converting code to int: {e}")
            self.error_message = "El código debe ser numérico."
            return
        try:
            original_pk = self.current_dispositivo.get("id", 0)
            if original_pk == 0:
                query = """
                    INSERT INTO public.dispositivos (codigo, descripcion, activo, enlinea)
                    VALUES (:codigo, :descripcion, :activo, :enlinea)
                """
                await self._execute_write(
                    query,
                    {
                        "codigo": code,
                        "descripcion": desc,
                        "activo": self.current_dispositivo.get("activo", True),
                        "enlinea": self.current_dispositivo.get("en_linea", False),
                    },
                    target_db="novalink",
                )
            else:
                query = """
                    UPDATE public.dispositivos
                    SET codigo = :new_codigo, descripcion = :descripcion, activo = :activo, enlinea = :enlinea
                    WHERE codigo = :original_pk
                """
                await self._execute_write(
                    query,
                    {
                        "original_pk": original_pk,
                        "new_codigo": code,
                        "descripcion": desc,
                        "activo": self.current_dispositivo.get("activo", True),
                        "enlinea": self.current_dispositivo.get("en_linea", False),
                    },
                    target_db="novalink",
                )
            self.show_dialog = False
            await self.load_dispositivos()
        except Exception as e:
            logging.exception(f"Error saving dispositivo: {e}")
            self.error_message = "Error al guardar. Verifique si el código ya existe."

    @rx.var
    def filtered_dispositivos(self) -> list[Dispositivo]:
        if not self.search_query:
            return self.dispositivos
        query = self.search_query.lower()
        return [
            d
            for d in self.dispositivos
            if query in d["codigo"].lower() or query in d["descripcion"].lower()
        ]