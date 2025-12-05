import reflex as rx
from typing import TypedDict
import logging
from app.states.database_state import DatabaseState
from sqlalchemy import text


class Justificacion(TypedDict):
    id: str
    descripcion: str
    cod_alterno: str
    dias_maximo: int
    horas_maximo: float
    dias_ingreso: int
    completafalta: bool
    completaatraso: bool
    justificacion: bool
    permiso: bool
    dias_habiles: bool
    documentoobligatorio: bool
    cargovacaciones: bool
    acumula_vacaciones: bool
    estado: bool


class TipoJustificacionesState(DatabaseState):
    justificaciones: list[Justificacion] = []
    show_inactive: bool = False
    show_modal: bool = False
    modal_justificacion: Justificacion = {
        "id": "0",
        "descripcion": "",
        "cod_alterno": "",
        "dias_maximo": 0,
        "horas_maximo": 0.0,
        "dias_ingreso": 0,
        "completafalta": False,
        "completaatraso": False,
        "justificacion": False,
        "permiso": False,
        "dias_habiles": False,
        "documentoobligatorio": False,
        "cargovacaciones": False,
        "acumula_vacaciones": False,
        "estado": True,
    }
    is_editing: bool = False

    @rx.var
    def filtered_justificaciones(self) -> list[Justificacion]:
        if self.show_inactive:
            return self.justificaciones
        return [j for j in self.justificaciones if j["estado"]]

    @rx.event
    def set_show_inactive(self, value: bool):
        self.show_inactive = value

    @rx.event
    async def on_load(self):
        """Load justifications from database on page load."""
        await self.load_justificaciones()

    @rx.event
    async def load_justificaciones(self):
        """Load justifications from 'detallejustificacion' table."""
        try:
            query = """
                SELECT 
                    codigo::text as id,
                    descripcion,
                    COALESCE(codalterno, '') as codalterno,
                    COALESCE(dias_maximo, 0) as dias_maximo,
                    COALESCE(horas_maximo, 0) as horas_maximo,
                    COALESCE(dias_ingreso, 0) as dias_ingreso,
                    COALESCE(completafalta, false) as completafalta,
                    COALESCE(completaatraso, false) as completaatraso,
                    COALESCE(justificacion, false) as justificacion,
                    COALESCE(permiso, false) as permiso,
                    COALESCE(dias_habiles, false) as dias_habiles,
                    COALESCE(documentoobligatorio, false) as documentoobligatorio,
                    COALESCE(cargovacaciones, false) as cargovacaciones,
                    COALESCE(acumula_vacaciones, false) as acumula_vacaciones,
                    activo as estado
                FROM detallejustificacion 
                WHERE codigo > 0
                ORDER BY descripcion ASC
            """
            results = await self._execute_query(query)
            if results:
                self.justificaciones = [
                    Justificacion(
                        id=row["id"],
                        descripcion=row["descripcion"],
                        cod_alterno=row["codalterno"],
                        dias_maximo=int(row["dias_maximo"]),
                        horas_maximo=float(row["horas_maximo"]),
                        dias_ingreso=int(row["dias_ingreso"]),
                        completafalta=bool(row["completafalta"]),
                        completaatraso=bool(row["completaatraso"]),
                        justificacion=bool(row["justificacion"]),
                        permiso=bool(row["permiso"]),
                        dias_habiles=bool(row["dias_habiles"]),
                        documentoobligatorio=bool(row["documentoobligatorio"]),
                        cargovacaciones=bool(row["cargovacaciones"]),
                        acumula_vacaciones=bool(row["acumula_vacaciones"]),
                        estado=bool(row["estado"]),
                    )
                    for row in results
                ]
            else:
                self.justificaciones = []
        except Exception as e:
            logging.exception(f"Error loading justificaciones: {e}")
            self.justificaciones = []

    def _get_empty_justificacion(self) -> Justificacion:
        return {
            "id": "0",
            "descripcion": "",
            "cod_alterno": "",
            "dias_maximo": 0,
            "horas_maximo": 0.0,
            "dias_ingreso": 0,
            "completafalta": False,
            "completaatraso": False,
            "justificacion": False,
            "permiso": False,
            "dias_habiles": False,
            "documentoobligatorio": False,
            "cargovacaciones": False,
            "acumula_vacaciones": False,
            "estado": True,
        }

    @rx.event
    def open_add_modal(self):
        self.is_editing = False
        self.modal_justificacion = self._get_empty_justificacion()
        self.show_modal = True

    @rx.event
    def open_edit_modal(self, justificacion: Justificacion):
        self.is_editing = True
        self.modal_justificacion = justificacion
        self.show_modal = True

    @rx.event
    def close_modal(self):
        self.show_modal = False

    @rx.event
    async def handle_submit(self, form_data: dict):
        descripcion_input = form_data.get("descripcion", "").strip()
        cod_alterno = form_data.get("cod_alterno", "").strip()
        try:
            dias_maximo = int(form_data.get("dias_maximo") or 0)
            horas_maximo = float(form_data.get("horas_maximo") or 0)
            dias_ingreso = int(form_data.get("dias_ingreso") or 0)
        except ValueError as e:
            logging.exception(f"Error validating numeric values: {e}")
            return rx.toast.error("Valores numéricos inválidos.")
        completafalta = bool(form_data.get("completafalta", False))
        completaatraso = bool(form_data.get("completaatraso", False))
        justificacion = bool(form_data.get("justificacion", False))
        permiso = bool(form_data.get("permiso", False))
        dias_habiles = bool(form_data.get("dias_habiles", False))
        documentoobligatorio = bool(form_data.get("documentoobligatorio", False))
        cargovacaciones = bool(form_data.get("cargovacaciones", False))
        acumula_vacaciones = bool(form_data.get("acumula_vacaciones", False))
        activo = bool(form_data.get("estado", False))
        if not descripcion_input:
            return rx.toast.error("La descripción es requerida.")
        from app.states.base_state import BaseState

        base_state = await self.get_state(BaseState)
        user_id = base_state.logged_user_id or 1
        params = {
            "desc": descripcion_input,
            "cod_alt": cod_alterno,
            "dias_max": dias_maximo,
            "horas_max": horas_maximo,
            "dias_ing": dias_ingreso,
            "c_falta": completafalta,
            "c_atraso": completaatraso,
            "justif": justificacion,
            "perm": permiso,
            "d_habiles": dias_habiles,
            "doc_oblig": documentoobligatorio,
            "c_vac": cargovacaciones,
            "a_vac": acumula_vacaciones,
            "activo": activo,
            "uid": user_id,
        }
        try:
            if self.is_editing and self.modal_justificacion["id"] != "0":
                query = """
                    UPDATE detallejustificacion
                    SET 
                        descripcion = :desc, 
                        codalterno = :cod_alt,
                        dias_maximo = :dias_max,
                        horas_maximo = :horas_max,
                        dias_ingreso = :dias_ing,
                        completafalta = :c_falta,
                        completaatraso = :c_atraso,
                        justificacion = :justif,
                        permiso = :perm,
                        dias_habiles = :d_habiles,
                        documentoobligatorio = :doc_oblig,
                        cargovacaciones = :c_vac,
                        acumula_vacaciones = :a_vac,
                        activo = :activo, 
                        usuario_modifica = :uid, 
                        fecha_modificacion = NOW()
                    WHERE codigo = :id
                """
                params["id"] = int(self.modal_justificacion["id"])
                await self._execute_write(query, params)
                rx.toast.success(f"Justificación actualizada correctamente.")
            else:
                next_id_result = await self._execute_query(
                    "SELECT COALESCE(MAX(codigo), 0) + 1 as next_id FROM detallejustificacion"
                )
                next_id = next_id_result[0]["next_id"] if next_id_result else 1
                params["id"] = next_id
                query = """
                    INSERT INTO detallejustificacion (
                        codigo, descripcion, codalterno, dias_maximo, horas_maximo, dias_ingreso,
                        completafalta, completaatraso, justificacion, permiso, dias_habiles, 
                        documentoobligatorio, cargovacaciones, acumula_vacaciones,
                        activo, usuario_crea, fecha_creacion, orden, usuario_modifica
                    )
                    VALUES (
                        :id, :desc, :cod_alt, :dias_max, :horas_max, :dias_ing,
                        :c_falta, :c_atraso, :justif, :perm, :d_habiles,
                        :doc_oblig, :c_vac, :a_vac,
                        :activo, :uid, NOW(), 0, 0
                    )
                """
                await self._execute_write(query, params)
                rx.toast.success(f"Justificación creada correctamente.")
            self.close_modal()
            await self.load_justificaciones()
        except Exception as e:
            logging.exception(f"Error saving justificacion: {e}")
            rx.toast.error(f"Error al guardar: {e}")

    @rx.event
    async def delete_justificacion(self, justificacion_id: str):
        from app.states.base_state import BaseState

        base_state = await self.get_state(BaseState)
        user_id = base_state.logged_user_id or 1
        try:
            query = """
                UPDATE detallejustificacion 
                SET activo = false, usuario_modifica = :uid, fecha_modificacion = NOW()
                WHERE codigo = :id
            """
            await self._execute_write(
                query, {"id": int(justificacion_id), "uid": user_id}
            )
            rx.toast.info("Justificación desactivada.")
            await self.load_justificaciones()
        except Exception as e:
            logging.exception(f"Error deleting justificacion: {e}")
            rx.toast.error(f"Error al eliminar: {e}")