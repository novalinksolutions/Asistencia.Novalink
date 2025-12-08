import reflex as rx
from typing import TypedDict, Optional
from app.states.database_state import DatabaseState
import logging
import math


class Transaccion(TypedDict):
    id: int
    dispositivo: str
    fechahora: str
    mensaje: str


class DispositivoFilter(TypedDict):
    id: int
    descripcion: str


class TransaccionesState(DatabaseState):
    """State for managing transactions view."""

    transacciones: list[Transaccion] = []
    dispositivos_filter: list[DispositivoFilter] = []
    selected_dispositivo_id: str = ""
    is_loading: bool = False
    current_page: int = 1
    items_per_page: int = 15
    total_items: int = 0

    @rx.var
    def total_pages(self) -> int:
        return (
            math.ceil(self.total_items / self.items_per_page)
            if self.items_per_page > 0
            else 1
        )

    @rx.var
    def has_next(self) -> bool:
        return self.current_page < self.total_pages

    @rx.var
    def has_prev(self) -> bool:
        return self.current_page > 1

    @rx.event
    async def on_load(self):
        """Load transactions data on page load."""
        logging.info("🔄 Loading Transacciones page...")
        await self._ensure_tables()
        await self.load_dispositivos_filter()
        await self.load_transacciones()

    async def _ensure_tables(self):
        """Ensure transacciones table exists."""
        query = """
            CREATE TABLE IF NOT EXISTS public.transacciones (
                id SERIAL PRIMARY KEY,
                dispositivo_id INTEGER REFERENCES public.dispositivos(id),
                fechahora TIMESTAMP DEFAULT NOW(),
                mensaje TEXT
            );
        """
        await self._execute_write(query, target_db="novalink")

    @rx.event
    async def load_dispositivos_filter(self):
        """Load devices for the filter dropdown."""
        try:
            query = "SELECT id, descripcion FROM public.dispositivos WHERE activo = true ORDER BY descripcion"
            results = await self._execute_query(query, target_db="novalink")
            self.dispositivos_filter = [
                DispositivoFilter(id=row["id"], descripcion=row["descripcion"])
                for row in results
            ]
        except Exception as e:
            logging.exception(f"Error loading devices filter: {e}")

    @rx.event
    async def load_transacciones(self):
        """Fetch transactions with filters and pagination."""
        self.is_loading = True
        try:
            conditions = ["DATE(t.fechahora) = CURRENT_DATE"]
            params = {}
            if self.selected_dispositivo_id and self.selected_dispositivo_id != "":
                conditions.append("t.dispositivo_id = :dev_id")
                params["dev_id"] = int(self.selected_dispositivo_id)
            where_clause = " AND ".join(conditions)
            count_query = f"SELECT COUNT(*) as count FROM public.transacciones t WHERE {where_clause}"
            count_res = await self._execute_query(
                count_query, params, target_db="novalink"
            )
            self.total_items = count_res[0]["count"] if count_res else 0
            offset = (self.current_page - 1) * self.items_per_page
            query = f"\n                SELECT \n                    t.id, \n                    d.descripcion as dispositivo_desc, \n                    t.fechahora, \n                    t.mensaje\n                FROM public.transacciones t\n                LEFT JOIN public.dispositivos d ON t.dispositivo_id = d.id\n                WHERE {where_clause}\n                ORDER BY t.fechahora DESC\n                LIMIT :limit OFFSET :offset\n            "
            params["limit"] = self.items_per_page
            params["offset"] = offset
            results = await self._execute_query(query, params, target_db="novalink")
            self.transacciones = [
                Transaccion(
                    id=row["id"],
                    dispositivo=row["dispositivo_desc"] or "Desconocido",
                    fechahora=row["fechahora"].strftime("%Y-%m-%d %H:%M:%S")
                    if row["fechahora"]
                    else "",
                    mensaje=row["mensaje"] or "",
                )
                for row in results
            ]
        except Exception as e:
            logging.exception(f"Error loading transacciones: {e}")
            self.transacciones = []
            self.total_items = 0
        finally:
            self.is_loading = False

    @rx.event
    def set_device_filter(self, value: str):
        self.selected_dispositivo_id = value
        self.current_page = 1
        return TransaccionesState.load_transacciones

    @rx.event
    def next_page(self):
        if self.has_next:
            self.current_page += 1
            return TransaccionesState.load_transacciones

    @rx.event
    def prev_page(self):
        if self.has_prev:
            self.current_page -= 1
            return TransaccionesState.load_transacciones