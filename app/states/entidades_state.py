import reflex as rx
from typing import TypedDict
import logging
from app.states.database_state import DatabaseState


class EntidadItem(TypedDict):
    codigo: int
    descripcion: str
    fecha_creacion: str
    usuario: str
    cod_alterno: str
    parent_id: int
    activo: bool


class NivelConfig(TypedDict):
    id: str
    label: str


class EntidadesState(DatabaseState):
    items: list[EntidadItem] = []
    niveles_config: list[NivelConfig] = []
    selected_nivel: str = "1"
    table_name: str = "niveladm1"
    search_query: str = ""
    show_inactive: bool = False
    selected_item: EntidadItem = {
        "codigo": 0,
        "descripcion": "",
        "fecha_creacion": "",
        "usuario": "",
        "cod_alterno": "",
        "parent_id": 0,
        "activo": True,
    }
    is_editing: bool = False
    parent_items_nivel1: list[dict] = []
    parent_items_nivel2: list[dict] = []
    parent_items_nivel3: list[dict] = []
    parent_items_nivel4: list[dict] = []
    selected_parent_nivel1: str = ""
    selected_parent_nivel2: str = ""
    selected_parent_nivel3: str = ""
    selected_parent_nivel4: str = ""

    @rx.var
    def filtered_items(self) -> list[EntidadItem]:
        items = self.items
        if not self.show_inactive:
            items = [i for i in items if i.get("activo", True)]
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
    def set_selected_parent_nivel1(self, value: str):
        self.selected_parent_nivel1 = value

    @rx.event
    def set_selected_parent_nivel2(self, value: str):
        self.selected_parent_nivel2 = value

    @rx.event
    def set_selected_parent_nivel3(self, value: str):
        self.selected_parent_nivel3 = value

    @rx.event
    def set_selected_parent_nivel4(self, value: str):
        self.selected_parent_nivel4 = value

    @rx.event
    def new_item(self):
        self.selected_item = {
            "codigo": 0,
            "descripcion": "",
            "fecha_creacion": "",
            "usuario": "",
            "cod_alterno": "",
            "parent_id": 0,
            "activo": True,
        }
        self.selected_parent_nivel1 = ""
        self.selected_parent_nivel2 = ""
        self.selected_parent_nivel3 = ""
        self.selected_parent_nivel4 = ""
        self.is_editing = True

    @rx.event
    def select_item(self, item: EntidadItem):
        self.selected_item = item
        self.is_editing = True
        parent_id_str = str(item.get("parent_id", 0))
        if self.selected_nivel == "2":
            self.selected_parent_nivel1 = parent_id_str
        elif self.selected_nivel == "3":
            self.selected_parent_nivel2 = parent_id_str
        elif self.selected_nivel == "4":
            self.selected_parent_nivel3 = parent_id_str
        elif self.selected_nivel == "5":
            self.selected_parent_nivel4 = parent_id_str
        elif self.selected_nivel == "cargos":
            self.selected_parent_nivel1 = parent_id_str
        elif self.selected_nivel == "grupos":
            self.selected_parent_nivel1 = parent_id_str
        elif self.selected_nivel == "atributo":
            self.selected_parent_nivel1 = parent_id_str

    @rx.event
    def cancel_edit(self):
        self.is_editing = False
        self.selected_item = {
            "codigo": 0,
            "descripcion": "",
            "fecha_creacion": "",
            "usuario": "",
            "cod_alterno": "",
            "parent_id": 0,
            "activo": True,
        }
        self.selected_parent_nivel1 = ""
        self.selected_parent_nivel2 = ""
        self.selected_parent_nivel3 = ""
        self.selected_parent_nivel4 = ""

    async def _ensure_activo_columns(self):
        """Ensure 'activo' column exists in all niveladm tables and cargos table."""
        if not self.has_db_connection:
            return
        from app.states.base_state import BaseState

        base_state = await self.get_state(BaseState)
        target_db = base_state.current_database_name or "novalink"
        for i in range(1, 6):
            try:
                query = f"ALTER TABLE public.niveladm{i} ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true"
                await self._execute_write(query, target_db=target_db)
            except Exception as e:
                logging.exception(
                    f"Migration: Could not add column 'activo' to niveladm{i}: {e}"
                )
        try:
            query = "ALTER TABLE public.cargos ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true"
            await self._execute_write(query, target_db=target_db)
        except Exception as e:
            logging.exception(
                f"Migration: Could not add column 'activo' to cargos: {e}"
            )
        try:
            query = "ALTER TABLE public.grupos ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true"
            await self._execute_write(query, target_db=target_db)
        except Exception as e:
            logging.exception(
                f"Migration: Could not add column 'activo' to grupos: {e}"
            )
        try:
            create_query = """
                CREATE TABLE IF NOT EXISTS public.atributotabularemp (
                    codigo INTEGER PRIMARY KEY,
                    descripcion TEXT,
                    niveladm1 INTEGER,
                    fechacreacion TIMESTAMP,
                    usuario TEXT,
                    activo BOOLEAN DEFAULT true
                )
            """
            await self._execute_write(create_query, target_db=target_db)
            query = "ALTER TABLE public.atributotabularemp ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true"
            await self._execute_write(query, target_db=target_db)
        except Exception as e:
            logging.exception(
                f"Migration: Could not ensure atributotabularemp table/column: {e}"
            )
        try:
            create_query = """
                CREATE TABLE IF NOT EXISTS public.tipoempleado (
                    codigo INTEGER PRIMARY KEY,
                    descripcion TEXT,
                    fechacreacion TIMESTAMP,
                    usuario TEXT,
                    activo BOOLEAN DEFAULT true
                )
            """
            await self._execute_write(create_query, target_db=target_db)
            query = "ALTER TABLE public.tipoempleado ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true"
            await self._execute_write(query, target_db=target_db)
        except Exception as e:
            logging.exception(
                f"Migration: Could not ensure tipoempleado table/column: {e}"
            )

    @rx.event
    async def on_load(self):
        """Load initial data."""
        logging.info("🔄 Cargando datos iniciales de Entidades...")
        await self._ensure_activo_columns()
        await self.load_config()
        self.table_name = f"niveladm{self.selected_nivel}"
        await self.load_items()
        await self.load_parent_items()

    @rx.event
    async def load_parent_items(self):
        """Load items from the parent level table based on current selection."""
        parent_table = ""
        target_list = ""
        if (
            self.selected_nivel == "cargos"
            or self.selected_nivel == "grupos"
            or self.selected_nivel == "atributo"
        ):
            parent_table = "niveladm1"
            target_list = "nivel1"
        elif self.selected_nivel == "tipoempleado":
            return
        else:
            try:
                parent_level = int(self.selected_nivel) - 1
                if parent_level < 1:
                    return
                parent_table = f"niveladm{parent_level}"
                target_list = f"nivel{parent_level}"
            except ValueError as e:
                logging.exception(f"Error parsing selected level: {e}")
                return
        try:
            query = f"SELECT codigo, descripcion FROM public.{parent_table} ORDER BY descripcion"
            results = await self._execute_query(query)
            items = [
                {"codigo": str(row["codigo"]), "descripcion": row["descripcion"]}
                for row in results
            ]
            if target_list == "nivel1":
                self.parent_items_nivel1 = items
            elif target_list == "nivel2":
                self.parent_items_nivel2 = items
            elif target_list == "nivel3":
                self.parent_items_nivel3 = items
            elif target_list == "nivel4":
                self.parent_items_nivel4 = items
        except Exception as e:
            logging.exception(f"Error loading parent items from {parent_table}: {e}")

    @rx.event
    async def load_items(self):
        if not self.table_name:
            return
        try:
            if self.selected_nivel == "cargos":
                query = """
                    SELECT 
                        codigo,
                        descripcion,
                        COALESCE(to_char(fechacreacion, 'YYYY-MM-DD HH24:MI'), '') as fecha_creacion,
                        COALESCE(usuario, '') as usuario,
                        '' as cod_alterno,
                        COALESCE(activo, true) as activo,
                        COALESCE(niveladm1, 0) as parent_id
                    FROM public.cargos 
                    ORDER BY descripcion ASC
                """
            elif self.selected_nivel == "grupos":
                query = """
                    SELECT 
                        codigo,
                        descripcion,
                        COALESCE(to_char(fechacreacion, 'YYYY-MM-DD HH24:MI'), '') as fecha_creacion,
                        COALESCE(usuario, '') as usuario,
                        '' as cod_alterno,
                        COALESCE(activo, true) as activo,
                        COALESCE(niveladm1, 0) as parent_id
                    FROM public.grupos 
                    ORDER BY descripcion ASC
                """
            elif self.selected_nivel == "tipoempleado":
                query = """
                    SELECT 
                        codigo,
                        descripcion,
                        COALESCE(to_char(fechacreacion, 'YYYY-MM-DD HH24:MI'), '') as fecha_creacion,
                        COALESCE(usuario, '') as usuario,
                        '' as cod_alterno,
                        COALESCE(activo, true) as activo,
                        0 as parent_id
                    FROM public.tipoempleado 
                    ORDER BY descripcion ASC
                """
            elif self.selected_nivel == "atributo":
                query = """
                    SELECT 
                        codigo,
                        descripcion,
                        COALESCE(to_char(fechacreacion, 'YYYY-MM-DD HH24:MI'), '') as fecha_creacion,
                        COALESCE(usuario, '') as usuario,
                        '' as cod_alterno,
                        COALESCE(activo, true) as activo,
                        COALESCE(niveladm1, 0) as parent_id
                    FROM public.atributotabularemp 
                    ORDER BY descripcion ASC
                """
            else:
                parent_col = ""
                if self.selected_nivel == "2":
                    parent_col = ", COALESCE(niveladm1, 0) as parent_id"
                elif self.selected_nivel == "3":
                    parent_col = ", COALESCE(niveladm2, 0) as parent_id"
                elif self.selected_nivel == "4":
                    parent_col = ", COALESCE(niveladm3, 0) as parent_id"
                elif self.selected_nivel == "5":
                    parent_col = ", COALESCE(niveladm4, 0) as parent_id"
                else:
                    parent_col = ", 0 as parent_id"
                query = f"\n                    SELECT \n                        codigo,\n                        descripcion,\n                        COALESCE(to_char(fechacreacion, 'YYYY-MM-DD HH24:MI'), '') as fecha_creacion,\n                        COALESCE(usuario, '') as usuario,\n                        COALESCE(codalterno, '') as cod_alterno,\n                        COALESCE(activo, true) as activo{parent_col}\n                    FROM public.{self.table_name} \n                    ORDER BY descripcion ASC\n                "
            results = await self._execute_query(query)
            self.items = [
                EntidadItem(
                    codigo=row["codigo"],
                    descripcion=row["descripcion"],
                    fecha_creacion=row["fecha_creacion"],
                    usuario=row["usuario"],
                    cod_alterno=row["cod_alterno"],
                    parent_id=int(row["parent_id"]),
                    activo=bool(row.get("activo", True)),
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
        parent_updates = {}
        try:
            if self.selected_nivel == "cargos":
                p_val = (
                    int(self.selected_parent_nivel1)
                    if self.selected_parent_nivel1
                    else 0
                )
                if p_val == 0:
                    return rx.toast.error("Debe seleccionar el nivel superior.")
                parent_updates["niveladm1"] = p_val
            elif self.selected_nivel == "grupos":
                p_val = (
                    int(self.selected_parent_nivel1)
                    if self.selected_parent_nivel1
                    else 0
                )
                if p_val == 0:
                    return rx.toast.error("Debe seleccionar el nivel superior.")
                parent_updates["niveladm1"] = p_val
            elif self.selected_nivel == "atributo":
                p_val = (
                    int(self.selected_parent_nivel1)
                    if self.selected_parent_nivel1
                    else 0
                )
                if p_val == 0:
                    return rx.toast.error("Debe seleccionar el nivel superior.")
                parent_updates["niveladm1"] = p_val
            elif self.selected_nivel == "2":
                p_val = (
                    int(self.selected_parent_nivel1)
                    if self.selected_parent_nivel1
                    else 0
                )
                if p_val == 0:
                    return rx.toast.error("Debe seleccionar el nivel superior.")
                parent_updates["niveladm1"] = p_val
            elif self.selected_nivel == "3":
                p_val = (
                    int(self.selected_parent_nivel2)
                    if self.selected_parent_nivel2
                    else 0
                )
                if p_val == 0:
                    return rx.toast.error("Debe seleccionar el nivel superior.")
                parent_updates["niveladm2"] = p_val
                query_ancestors = (
                    "SELECT niveladm1 FROM public.niveladm2 WHERE codigo = :id"
                )
                ancestors = await self._execute_query(query_ancestors, {"id": p_val})
                if ancestors:
                    parent_updates["niveladm1"] = ancestors[0]["niveladm1"]
            elif self.selected_nivel == "4":
                p_val = (
                    int(self.selected_parent_nivel3)
                    if self.selected_parent_nivel3
                    else 0
                )
                if p_val == 0:
                    return rx.toast.error("Debe seleccionar el nivel superior.")
                parent_updates["niveladm3"] = p_val
                query_ancestors = "SELECT niveladm1, niveladm2 FROM public.niveladm3 WHERE codigo = :id"
                ancestors = await self._execute_query(query_ancestors, {"id": p_val})
                if ancestors:
                    parent_updates["niveladm1"] = ancestors[0]["niveladm1"]
                    parent_updates["niveladm2"] = ancestors[0]["niveladm2"]
            elif self.selected_nivel == "5":
                p_val = (
                    int(self.selected_parent_nivel4)
                    if self.selected_parent_nivel4
                    else 0
                )
                if p_val == 0:
                    return rx.toast.error("Debe seleccionar el nivel superior.")
                parent_updates["niveladm4"] = p_val
                query_ancestors = "SELECT niveladm1, niveladm2, niveladm3 FROM public.niveladm4 WHERE codigo = :id"
                ancestors = await self._execute_query(query_ancestors, {"id": p_val})
                if ancestors:
                    parent_updates["niveladm1"] = ancestors[0]["niveladm1"]
                    parent_updates["niveladm2"] = ancestors[0]["niveladm2"]
                    parent_updates["niveladm3"] = ancestors[0]["niveladm3"]
            from app.states.base_state import BaseState

            base_state = await self.get_state(BaseState)
            current_user = base_state.logged_user_name or "unknown"
            if self.selected_nivel == "cargos":
                if self.selected_item["codigo"] == 0:
                    next_id_res = await self._execute_query(
                        "SELECT COALESCE(MAX(codigo), 0) + 1 as next_id FROM public.cargos"
                    )
                    next_id = next_id_res[0]["next_id"] if next_id_res else 1
                    query = """
                        INSERT INTO public.cargos 
                        (codigo, descripcion, niveladm1, fechacreacion, usuario, activo)
                        VALUES (:id, :desc, :p_id, NOW(), :user, :active)
                    """
                    await self._execute_write(
                        query,
                        {
                            "id": next_id,
                            "desc": self.selected_item["descripcion"],
                            "p_id": parent_updates["niveladm1"],
                            "user": current_user,
                            "active": self.selected_item["activo"],
                        },
                    )
                    rx.toast.success("Cargo creado correctamente.")
                else:
                    query = """
                        UPDATE public.cargos 
                        SET descripcion = :desc, 
                            niveladm1 = :p_id, 
                            usuario = :user, 
                            activo = :active
                        WHERE codigo = :id
                    """
                    await self._execute_write(
                        query,
                        {
                            "id": self.selected_item["codigo"],
                            "desc": self.selected_item["descripcion"],
                            "p_id": parent_updates["niveladm1"],
                            "user": current_user,
                            "active": self.selected_item["activo"],
                        },
                    )
                    rx.toast.success("Cargo actualizado correctamente.")
            elif self.selected_nivel == "grupos":
                if self.selected_item["codigo"] == 0:
                    next_id_res = await self._execute_query(
                        "SELECT COALESCE(MAX(codigo), 0) + 1 as next_id FROM public.grupos"
                    )
                    next_id = next_id_res[0]["next_id"] if next_id_res else 1
                    query = """
                        INSERT INTO public.grupos 
                        (codigo, descripcion, niveladm1, fechacreacion, usuario, activo)
                        VALUES (:id, :desc, :p_id, NOW(), :user, :active)
                    """
                    await self._execute_write(
                        query,
                        {
                            "id": next_id,
                            "desc": self.selected_item["descripcion"],
                            "p_id": parent_updates["niveladm1"],
                            "user": current_user,
                            "active": self.selected_item["activo"],
                        },
                    )
                    rx.toast.success("Grupo creado correctamente.")
                else:
                    query = """
                        UPDATE public.grupos 
                        SET descripcion = :desc, 
                            niveladm1 = :p_id, 
                            usuario = :user, 
                            activo = :active
                        WHERE codigo = :id
                    """
                    await self._execute_write(
                        query,
                        {
                            "id": self.selected_item["codigo"],
                            "desc": self.selected_item["descripcion"],
                            "p_id": parent_updates["niveladm1"],
                            "user": current_user,
                            "active": self.selected_item["activo"],
                        },
                    )
                    rx.toast.success("Grupo actualizado correctamente.")
            elif self.selected_nivel == "tipoempleado":
                if self.selected_item["codigo"] == 0:
                    next_id_res = await self._execute_query(
                        "SELECT COALESCE(MAX(codigo), 0) + 1 as next_id FROM public.tipoempleado"
                    )
                    next_id = next_id_res[0]["next_id"] if next_id_res else 1
                    query = """
                        INSERT INTO public.tipoempleado 
                        (codigo, descripcion, fechacreacion, usuario, activo)
                        VALUES (:id, :desc, NOW(), :user, :active)
                    """
                    await self._execute_write(
                        query,
                        {
                            "id": next_id,
                            "desc": self.selected_item["descripcion"],
                            "user": current_user,
                            "active": self.selected_item["activo"],
                        },
                    )
                    rx.toast.success("Tipo de empleado creado correctamente.")
                else:
                    query = """
                        UPDATE public.tipoempleado 
                        SET descripcion = :desc, 
                            usuario = :user, 
                            activo = :active
                        WHERE codigo = :id
                    """
                    await self._execute_write(
                        query,
                        {
                            "id": self.selected_item["codigo"],
                            "desc": self.selected_item["descripcion"],
                            "user": current_user,
                            "active": self.selected_item["activo"],
                        },
                    )
                    rx.toast.success("Tipo de empleado actualizado correctamente.")
            elif self.selected_nivel == "atributo":
                if self.selected_item["codigo"] == 0:
                    next_id_res = await self._execute_query(
                        "SELECT COALESCE(MAX(codigo), 0) + 1 as next_id FROM public.atributotabularemp"
                    )
                    next_id = next_id_res[0]["next_id"] if next_id_res else 1
                    query = """
                        INSERT INTO public.atributotabularemp 
                        (codigo, descripcion, niveladm1, fechacreacion, usuario, activo)
                        VALUES (:id, :desc, :p_id, NOW(), :user, :active)
                    """
                    await self._execute_write(
                        query,
                        {
                            "id": next_id,
                            "desc": self.selected_item["descripcion"],
                            "p_id": parent_updates["niveladm1"],
                            "user": current_user,
                            "active": self.selected_item["activo"],
                        },
                    )
                    rx.toast.success("Registro adicional creado correctamente.")
                else:
                    query = """
                        UPDATE public.atributotabularemp 
                        SET descripcion = :desc, 
                            niveladm1 = :p_id, 
                            usuario = :user, 
                            activo = :active
                        WHERE codigo = :id
                    """
                    await self._execute_write(
                        query,
                        {
                            "id": self.selected_item["codigo"],
                            "desc": self.selected_item["descripcion"],
                            "p_id": parent_updates["niveladm1"],
                            "user": current_user,
                            "active": self.selected_item["activo"],
                        },
                    )
                    rx.toast.success("Registro adicional actualizado correctamente.")
            elif self.selected_item["codigo"] == 0:
                next_id_res = await self._execute_query(
                    f"SELECT COALESCE(MAX(codigo), 0) + 1 as next_id FROM public.{self.table_name}"
                )
                next_id = next_id_res[0]["next_id"] if next_id_res else 1
                cols = "codigo, descripcion, usuario, fechacreacion, activo"
                vals = ":id, :desc, :user, NOW(), :active"
                params = {
                    "id": next_id,
                    "desc": self.selected_item["descripcion"],
                    "user": current_user,
                    "active": self.selected_item["activo"],
                }
                for col, val in parent_updates.items():
                    cols += f", {col}"
                    vals += f", :{col}"
                    params[col] = val
                query = f"INSERT INTO public.{self.table_name} ({cols}) VALUES ({vals})"
                await self._execute_write(query, params)
                rx.toast.success("Registro creado correctamente.")
            else:
                set_clause = "descripcion = :desc, activo = :active"
                params = {
                    "id": self.selected_item["codigo"],
                    "desc": self.selected_item["descripcion"],
                    "active": self.selected_item["activo"],
                }
                for col, val in parent_updates.items():
                    set_clause += f", {col} = :{col}"
                    params[col] = val
                query = f"UPDATE public.{self.table_name} SET {set_clause} WHERE codigo = :id"
                await self._execute_write(query, params)
                rx.toast.success("Registro actualizado correctamente.")
            self.cancel_edit()
            await self.load_items()
        except Exception as e:
            logging.exception(f"Error saving item to {self.table_name}: {e}")
            rx.toast.error(f"Error al guardar: {e}")

    @rx.event
    async def load_config(self):
        """Load enabled levels and their labels from parameters."""
        if not self.has_db_connection:
            self.niveles_config = [
                {"id": "1", "label": "Empresa"},
                {"id": "2", "label": "Sucursal"},
                {"id": "3", "label": "Departamento"},
                {"id": "cargos", "label": "Cargos"},
                {"id": "grupos", "label": "Grupos"},
            ]
            return
        try:
            query = "SELECT codigo, valor FROM public.parametros WHERE codigo IN (4, 5, 8, 11, 14, 17, 35, 36)"
            results = await self._execute_query(query, target_db="novalink")
            params = {row["codigo"]: row["valor"] for row in results}
            count = int(params.get(4, "5"))
            configs = []
            label_codes = {1: 5, 2: 8, 3: 11, 4: 14, 5: 17}
            for i in range(1, count + 1):
                code = label_codes.get(i)
                label = params.get(code, f"Nivel {i}")
                configs.append({"id": str(i), "label": label})
            configs.append({"id": "cargos", "label": "Cargos"})
            configs.append({"id": "grupos", "label": "Grupos"})
            configs.append({"id": "tipoempleado", "label": "Tipo Empleado"})
            if params.get(35, "0") == "1":
                label_attr = params.get(36, "Atributo Adicional")
                configs.append({"id": "atributo", "label": label_attr})
            self.niveles_config = configs
            try:
                available_ids = [c["id"] for c in configs]
                if self.selected_nivel not in available_ids:
                    logging.warning(
                        f"Nivel seleccionado '{self.selected_nivel}' no válido. Reseteando a '1'."
                    )
                    self.selected_nivel = "1"
            except Exception as e:
                logging.exception(f"Error validating selected level: {e}")
                self.selected_nivel = "1"
        except Exception as e:
            logging.exception(f"Error loading niveles config: {e}")
            self.niveles_config = [{"id": "1", "label": "Nivel 1"}]

    @rx.event
    async def set_selected_nivel(self, value: str):
        self.selected_nivel = value
        if value == "cargos":
            self.table_name = "cargos"
        elif value == "grupos":
            self.table_name = "grupos"
        elif value == "tipoempleado":
            self.table_name = "tipoempleado"
        elif value == "atributo":
            self.table_name = "atributotabularemp"
        else:
            self.table_name = f"niveladm{value}"
        self.cancel_edit()
        await self.load_items()
        await self.load_parent_items()