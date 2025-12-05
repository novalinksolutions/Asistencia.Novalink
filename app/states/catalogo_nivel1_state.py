import reflex as rx
from app.states.catalogo_base_state import CatalogoBaseState


class CatalogoNivel1State(CatalogoBaseState):
    table_name: str = "niveladm1"

    @rx.event
    async def on_load(self):
        await self.load_items()