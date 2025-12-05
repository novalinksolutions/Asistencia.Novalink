import reflex as rx
from app.states.database_state import DatabaseState


class EmpleadosState(DatabaseState):
    @rx.event
    async def on_load(self):
        pass