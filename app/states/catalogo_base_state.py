import reflex as rx
from typing import TypedDict, Optional
import logging
from app.states.database_state import DatabaseState
from sqlalchemy import text


class CatalogoItem(TypedDict):
    codigo: int
    descripcion: str
    activo: bool
    fecha_creacion: str
    fecha_modificacion: str


class CatalogoBaseState(DatabaseState):
    """Base state for catalog CRUD operations."""

    items: list[CatalogoItem] = []
    selected_item: CatalogoItem = {
        "codigo": 0,
        "descripcion": "",
        "activo": True,
        "fecha_creacion": "",
        "fecha_modificacion": "",
    }
    show_inactive: bool = False
    is_editing: bool = False
    search_query: str = ""
    table_name: str = ""

    @rx.var
    def filtered_items(self) -> list[CatalogoItem]:
        items = self.items
        if not self.show_inactive:
            items = [i for i in items if i["activo"]]
        if self.search_query:
            q = self.search_query.lower()
            items = [i for i in items if q in i["descripcion"].lower()]
        return items

    @rx.event
    def set_show_inactive(self, value: bool):
        self.show_inactive = value

    @rx.event
    def set_search_query(self, value: str):
        self.search_query = value

    @rx.event
    def set_selected_item_description(self, value: str):
        self.selected_item["descripcion"] = value

    @rx.event
    def set_selected_item_active(self, checked: bool):
        self.selected_item["activo"] = checked

    @rx.event
    def new_item(self):
        self.selected_item = {
            "codigo": 0,
            "descripcion": "",
            "activo": True,
            "fecha_creacion": "",
            "fecha_modificacion": "",
        }
        self.is_editing = True

    @rx.event
    def select_item(self, item: CatalogoItem):
        self.selected_item = item
        self.is_editing = True

    @rx.event
    def cancel_edit(self):
        self.is_editing = False
        self.selected_item = {
            "codigo": 0,
            "descripcion": "",
            "activo": True,
            "fecha_creacion": "",
            "fecha_modificacion": "",
        }

    @rx.event
    async def load_items(self):
        if not self.table_name:
            return
        try:
            query = f"\n                SELECT \n                    codigo,\n                    descripcion,\n                    activo,\n                    COALESCE(to_char(fechacreacion, 'YYYY-MM-DD HH24:MI'), '') as fecha_creacion,\n                    COALESCE(to_char(fechamodificacion, 'YYYY-MM-DD HH24:MI'), '') as fecha_modificacion\n                FROM public.{self.table_name} \n                ORDER BY descripcion ASC\n            "
            results = await self._execute_query(query)
            self.items = [
                CatalogoItem(
                    codigo=row["codigo"],
                    descripcion=row["descripcion"],
                    activo=bool(row["activo"]),
                    fecha_creacion=row["fecha_creacion"],
                    fecha_modificacion=row["fecha_modificacion"],
                )
                for row in results
            ]
        except Exception as e:
            logging.exception(f"Error loading items from {self.table_name}: {e}")
            self.items = []

    @rx.event
    async def save_item(self):
        if not self.selected_item["descripcion"].strip():
            return rx.toast.error("La descripción es obligatoria.")
        from app.states.base_state import BaseState

        base_state = await self.get_state(BaseState)
        user_id = base_state.logged_user_id or 1
        try:
            if self.selected_item["codigo"] == 0:
                next_id_res = await self._execute_query(
                    f"SELECT COALESCE(MAX(codigo), 0) + 1 as next_id FROM public.{self.table_name}"
                )
                next_id = next_id_res[0]["next_id"] if next_id_res else 1
                query = f"\n                    INSERT INTO public.{self.table_name} \n                    (codigo, descripcion, activo, usuariocrea, fechacreacion)\n                    VALUES\n                    (:id, :desc, :active, :uid, NOW())\n                "
                await self._execute_write(
                    query,
                    {
                        "id": next_id,
                        "desc": self.selected_item["descripcion"],
                        "active": self.selected_item["activo"],
                        "uid": user_id,
                    },
                )
                rx.toast.success("Registro creado correctamente.")
            else:
                query = f"\n                    UPDATE public.{self.table_name}\n                    SET \n                        descripcion = :desc, \n                        activo = :active, \n                        usuariomodifica = :uid, \n                        fechamodificacion = NOW()\n                    WHERE codigo = :id\n                "
                await self._execute_write(
                    query,
                    {
                        "id": self.selected_item["codigo"],
                        "desc": self.selected_item["descripcion"],
                        "active": self.selected_item["activo"],
                        "uid": user_id,
                    },
                )
                rx.toast.success("Registro actualizado correctamente.")
            self.cancel_edit()
            await self.load_items()
        except Exception as e:
            logging.exception(f"Error saving item to {self.table_name}: {e}")
            rx.toast.error(f"Error al guardar: {e}")