import reflex as rx
from typing import TypedDict, Any, Optional
import logging
import hashlib
import datetime
from app.states.database_state import DatabaseState


class Employee(TypedDict):
    id: int
    cedula: str
    nombres: str
    apellidos: str
    correoelectronico: str
    transporte: bool
    alimentacion: bool
    zona: int
    fechacalculovacaciones: str
    fechaingreso: str
    ganarecargonocturno: bool
    ganasobretiempo: bool
    stconautorizacion: bool
    ganarecargodialibre: bool
    offline: bool
    niveladm1: int
    niveladm2: int
    niveladm3: int
    niveladm4: int
    niveladm5: int
    cargo: int
    tipo: int
    grupo: int
    atributotabular: int
    atributotexto: str
    accesoweb: bool
    pwd: str
    activo: bool
    nivelautorizacion: int
    fechacreacion: str
    fechamodificacion: str


class CatalogItem(TypedDict):
    id: int
    descripcion: str


class HierarchyItem(TypedDict):
    id: int
    name: str


class EmpleadosState(DatabaseState):
    employees: list[Employee] = []
    selected_employee: Employee = {
        "id": 0,
        "cedula": "",
        "nombres": "",
        "apellidos": "",
        "correoelectronico": "",
        "transporte": False,
        "alimentacion": False,
        "zona": 0,
        "fechacalculovacaciones": "",
        "fechaingreso": "",
        "ganarecargonocturno": False,
        "ganasobretiempo": False,
        "stconautorizacion": False,
        "ganarecargodialibre": False,
        "offline": False,
        "niveladm1": 0,
        "niveladm2": 0,
        "niveladm3": 0,
        "niveladm4": 0,
        "niveladm5": 0,
        "cargo": 0,
        "tipo": 0,
        "grupo": 0,
        "atributotabular": 0,
        "atributotexto": "",
        "accesoweb": False,
        "pwd": "12345678",
        "activo": True,
        "nivelautorizacion": 0,
        "fechacreacion": "",
        "fechamodificacion": "",
    }
    cat_nivel1: list[CatalogItem] = []
    cat_nivel2: list[CatalogItem] = []
    cat_nivel3: list[CatalogItem] = []
    cat_nivel4: list[CatalogItem] = []
    cat_nivel5: list[CatalogItem] = []
    cat_cargos: list[CatalogItem] = []
    cat_grupos: list[CatalogItem] = []
    cat_tipos: list[CatalogItem] = []
    cat_attr_tabular: list[CatalogItem] = []
    search_query: str = ""
    show_inactive: bool = False
    is_editing: bool = False
    niveles_habilitados: int = 5
    labels_niveles: dict[str, str] = {
        "1": "Nivel 1",
        "2": "Nivel 2",
        "3": "Nivel 3",
        "4": "Nivel 4",
        "5": "Nivel 5",
    }
    has_attr_tabular: bool = False
    has_attr_texto: bool = False
    label_attr_tabular: str = "Atributo Tabular"
    label_attr_texto: str = "Atributo Texto"
    is_email_editable: bool = False
    editing_employee_id: int = 0
    id_input: str = ""
    superiores: list[HierarchyItem] = []
    subalternos: list[HierarchyItem] = []
    available_employees: list[HierarchyItem] = []
    can_authorize: bool = False
    show_hierarchy_dialog: bool = False
    hierarchy_dialog_type: str = "superior"
    selected_list_superior_id: int = 0
    selected_list_subordinate_id: int = 0
    employee_to_add_id: str = ""
    hierarchy_search_query: str = ""

    @rx.var
    def filtered_hierarchy_employees(self) -> list[HierarchyItem]:
        if len(self.hierarchy_search_query) < 3:
            return []
        query = self.hierarchy_search_query.lower()
        return [emp for emp in self.available_employees if query in emp["name"].lower()]

    @rx.var
    def selected_hierarchy_employee_name(self) -> str:
        if not self.employee_to_add_id:
            return ""
        for emp in self.available_employees:
            if str(emp["id"]) == self.employee_to_add_id:
                return emp["name"]
        return ""

    @rx.event
    def set_hierarchy_search_query(self, value: str):
        self.hierarchy_search_query = value

    @rx.event
    def select_hierarchy_employee_from_search(self, emp_id: int):
        self.employee_to_add_id = str(emp_id)

    @rx.var
    def formatted_id(self) -> str:
        """Return the ID padded with zeros to 10 digits."""
        return f"{self.selected_employee['id']:010d}"

    @rx.var
    def masked_email(self) -> str:
        email = self.selected_employee["correoelectronico"]
        if not email or "@" not in email:
            return email or ""
        try:
            user_part, domain_part = email.split("@", 1)
            if len(user_part) > 4:
                masked_user = user_part[:4] + "xxxx" + user_part[-1]
            else:
                masked_user = user_part
            if "." in domain_part:
                domain_host, domain_ext = domain_part.split(".", 1)
                masked_domain = (
                    domain_host[0] + "xxxx." + domain_ext
                    if domain_host
                    else domain_part
                )
            else:
                masked_domain = domain_part
            return f"{masked_user}@{masked_domain}"
        except Exception as e:
            logging.exception(f"Error masking email: {e}")
            return email

    @rx.event
    def toggle_email_editable(self):
        self.is_email_editable = not self.is_email_editable

    @rx.var
    def recent_employees(self) -> list[Employee]:
        if not self.employees:
            return []
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        @rx.event
        def get_sort_date(e: Employee):
            d1 = e.get("fechacreacion") or ""
            d2 = e.get("fechamodificacion") or ""
            return max(d1, d2)

        recent = [e for e in self.employees if get_sort_date(e) >= cutoff]
        recent.sort(key=get_sort_date, reverse=True)
        return recent[:10]

    @rx.var
    def filtered_employees(self) -> list[Employee]:
        if len(self.search_query) < 3:
            return self.recent_employees
        items = self.employees
        if not self.show_inactive:
            items = [e for e in items if e["activo"]]
        q = self.search_query.lower()
        items = [
            e
            for e in items
            if q in e["nombres"].lower()
            or q in e["apellidos"].lower()
            or q in e["cedula"].lower()
        ]
        return items

    @rx.var
    def form_title(self) -> str:
        return (
            "Editar Empleado" if self.selected_employee["id"] != 0 else "Nuevo Empleado"
        )

    @rx.var
    def is_pwd_enabled(self) -> bool:
        return self.selected_employee["accesoweb"]

    @rx.event
    def set_search_query(self, value: str):
        self.search_query = value

    @rx.event
    def set_show_inactive(self, value: bool):
        self.show_inactive = value

    @rx.event
    def set_field(self, field: str, value: Any):
        self.selected_employee[field] = value

    @rx.event
    def set_int_field(self, field: str, value: str):
        try:
            self.selected_employee[field] = int(value)
        except ValueError as e:
            logging.exception(f"Error converting field {field} to int: {e}")

    @rx.event
    def toggle_bool_field(self, field: str, checked: bool):
        self.selected_employee[field] = checked

    @rx.event
    def set_id_field(self, value: str):
        """Set ID ensuring it is numeric and max 10 digits, storing raw input."""
        digits = "".join(filter(str.isdigit, value))
        if len(digits) > 10:
            digits = digits[:10]
        self.id_input = digits
        if digits:
            self.selected_employee["id"] = int(digits)
        else:
            self.selected_employee["id"] = 0

    @rx.event
    def new_employee(self):
        self.editing_employee_id = 0
        self.id_input = ""
        self.superiores = []
        self.subalternos = []
        self.can_authorize = False
        self.selected_employee = {
            "id": 0,
            "cedula": "",
            "nombres": "",
            "apellidos": "",
            "correoelectronico": "",
            "transporte": False,
            "alimentacion": False,
            "zona": 0,
            "fechacalculovacaciones": "",
            "fechaingreso": "",
            "ganarecargonocturno": False,
            "ganasobretiempo": False,
            "stconautorizacion": False,
            "ganarecargodialibre": False,
            "offline": False,
            "niveladm1": 0,
            "niveladm2": 0,
            "niveladm3": 0,
            "niveladm4": 0,
            "niveladm5": 0,
            "cargo": 0,
            "tipo": 0,
            "grupo": 0,
            "atributotabular": 0,
            "atributotexto": "",
            "accesoweb": False,
            "pwd": "12345678",
            "activo": True,
            "nivelautorizacion": 0,
            "fechacreacion": "",
            "fechamodificacion": "",
        }
        self.is_email_editable = True
        self.is_editing = True

    @rx.event
    async def select_employee(self, employee: Employee):
        self.editing_employee_id = employee["id"]
        self.selected_employee = employee.copy()
        self.id_input = f"{employee['id']:010d}"
        self.is_editing = True
        self.is_email_editable = False
        await self.load_hierarchy()

    @rx.event
    def cancel_edit(self):
        self.is_editing = False
        self.is_email_editable = False
        self.new_employee()

    async def _ensure_tables(self):
        if not self.has_db_connection:
            return
        try:
            query = """
                CREATE TABLE IF NOT EXISTS public.empleados (
                    id BIGINT PRIMARY KEY,
                    cedula VARCHAR(20),
                    apellidos VARCHAR(50),
                    nombres VARCHAR(50),
                    correoelectronico VARCHAR(50),
                    telefono VARCHAR(50) DEFAULT '',
                    direccion VARCHAR(200) DEFAULT '',
                    fechanacimiento DATE DEFAULT NOW(),
                    solotarjeta BOOLEAN DEFAULT false,
                    ganarecargonocturno BOOLEAN DEFAULT false,
                    ganasobretiempo BOOLEAN DEFAULT false,
                    stconautorizacion BOOLEAN DEFAULT false,
                    ganarecargodialibre BOOLEAN DEFAULT false,
                    offline BOOLEAN DEFAULT false,
                    niveladm1 BIGINT DEFAULT 0,
                    niveladm2 BIGINT DEFAULT 0,
                    niveladm3 BIGINT DEFAULT 0,
                    niveladm4 BIGINT DEFAULT 0,
                    niveladm5 BIGINT DEFAULT 0,
                    cargo BIGINT DEFAULT 0,
                    tipo BIGINT DEFAULT 0,
                    grupo BIGINT DEFAULT 0,
                    atributotabular BIGINT DEFAULT 0,
                    atributotexto VARCHAR(10),
                    accesoweb BOOLEAN DEFAULT false,
                    pwd TEXT,
                    activo BOOLEAN DEFAULT true,
                    fechacreacion TIMESTAMP DEFAULT NOW(),
                    usuario BIGINT DEFAULT 1,
                    usuariocrea BIGINT DEFAULT 1,
                    fechamodificacion TIMESTAMP,
                    usuariomodifica BIGINT,
                    nivelautorizacion SMALLINT DEFAULT 0
                )
            """
            await self._execute_write(query, target_db="novalink")
            try:
                await self._execute_write(
                    "ALTER TABLE public.empleados DISABLE TRIGGER tr_log_empleados",
                    target_db="novalink",
                )
            except Exception as e:
                logging.exception(
                    f"Could not disable trigger tr_log_empleados (might not exist): {e}"
                )
            try:
                alter_query_usr = "ALTER TABLE public.empleados ADD COLUMN IF NOT EXISTS usuario BIGINT DEFAULT 1"
                await self._execute_write(alter_query_usr, target_db="novalink")
                alter_query = "ALTER TABLE public.empleados ADD COLUMN IF NOT EXISTS grupo BIGINT DEFAULT 0"
                await self._execute_write(alter_query, target_db="novalink")
                alter_query_tel = "ALTER TABLE public.empleados ADD COLUMN IF NOT EXISTS telefono VARCHAR(50) DEFAULT ''"
                await self._execute_write(alter_query_tel, target_db="novalink")
                mod_query_tel = "ALTER TABLE public.empleados ALTER COLUMN telefono TYPE VARCHAR(50), ALTER COLUMN telefono SET DEFAULT ''"
                await self._execute_write(mod_query_tel, target_db="novalink")
                fix_nulls_tel = (
                    "UPDATE public.empleados SET telefono = '' WHERE telefono IS NULL"
                )
                await self._execute_write(fix_nulls_tel, target_db="novalink")
                alter_query_dir = "ALTER TABLE public.empleados ADD COLUMN IF NOT EXISTS direccion VARCHAR(200) DEFAULT ''"
                await self._execute_write(alter_query_dir, target_db="novalink")
                mod_query_dir = "ALTER TABLE public.empleados ALTER COLUMN direccion TYPE VARCHAR(200), ALTER COLUMN direccion SET DEFAULT ''"
                await self._execute_write(mod_query_dir, target_db="novalink")
                fix_nulls_dir = (
                    "UPDATE public.empleados SET direccion = '' WHERE direccion IS NULL"
                )
                await self._execute_write(fix_nulls_dir, target_db="novalink")
                alter_query_fnac = "ALTER TABLE public.empleados ADD COLUMN IF NOT EXISTS fechanacimiento DATE DEFAULT NOW()"
                await self._execute_write(alter_query_fnac, target_db="novalink")
                alter_query_st = "ALTER TABLE public.empleados ADD COLUMN IF NOT EXISTS solotarjeta BOOLEAN DEFAULT false"
                await self._execute_write(alter_query_st, target_db="novalink")
                fix_nulls_st = "UPDATE public.empleados SET solotarjeta = false WHERE solotarjeta IS NULL"
                await self._execute_write(fix_nulls_st, target_db="novalink")
                alter_query_auth = "ALTER TABLE public.empleados ADD COLUMN IF NOT EXISTS nivelautorizacion SMALLINT DEFAULT 0"
                await self._execute_write(alter_query_auth, target_db="novalink")
                fix_nulls_query = "UPDATE public.empleados SET nivelautorizacion = 0 WHERE nivelautorizacion IS NULL"
                await self._execute_write(fix_nulls_query, target_db="novalink")
                force_default_query = "ALTER TABLE public.empleados ALTER COLUMN nivelautorizacion SET DEFAULT 0"
                await self._execute_write(force_default_query, target_db="novalink")
            finally:
                try:
                    await self._execute_write(
                        "ALTER TABLE public.empleados ENABLE TRIGGER tr_log_empleados",
                        target_db="novalink",
                    )
                except Exception as e:
                    logging.exception(f"Could not enable trigger tr_log_empleados: {e}")
        except Exception as e:
            logging.exception(f"Error ensuring empleados table: {e}")

    @rx.event
    async def on_load(self):
        await self._ensure_tables()
        await self._ensure_jerarquias_table()
        await self._drop_fk_constraints()
        await self.load_config()
        await self.load_catalogs()
        await self.load_employees()

    async def _drop_fk_constraints(self):
        """Drop foreign key constraints to allow saving with default values (0)."""
        if not self.has_db_connection:
            return
        try:
            query_find = """
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'empleados' 
                AND constraint_type = 'FOREIGN KEY' 
                AND table_schema = 'public'
            """
            results = await self._execute_query(query_find, target_db="novalink")
            for row in results:
                constraint = row["constraint_name"]
                logging.info(f"Dropping FK constraint: {constraint}")
                drop_query = (
                    f'ALTER TABLE public.empleados DROP CONSTRAINT "{constraint}"'
                )
                await self._execute_write(drop_query, target_db="novalink")
        except Exception as e:
            logging.exception(f"Error dropping foreign keys: {e}")

    async def _ensure_jerarquias_table(self):
        if not self.has_db_connection:
            return
        try:
            query = """
                CREATE TABLE IF NOT EXISTS public.jerarquias (
                    id SERIAL PRIMARY KEY,
                    empleado_superior BIGINT,
                    empleado_subordinado BIGINT,
                    fechacreacion TIMESTAMP DEFAULT NOW(),
                    usuario BIGINT
                )
            """
            await self._execute_write(query, target_db="novalink")
            alter_superior = "ALTER TABLE public.jerarquias ADD COLUMN IF NOT EXISTS empleado_superior BIGINT"
            await self._execute_write(alter_superior, target_db="novalink")
            alter_subordinado = "ALTER TABLE public.jerarquias ADD COLUMN IF NOT EXISTS empleado_subordinado BIGINT"
            await self._execute_write(alter_subordinado, target_db="novalink")
            alter_fecha = "ALTER TABLE public.jerarquias ADD COLUMN IF NOT EXISTS fechacreacion TIMESTAMP DEFAULT NOW()"
            await self._execute_write(alter_fecha, target_db="novalink")
            alter_usuario = (
                "ALTER TABLE public.jerarquias ADD COLUMN IF NOT EXISTS usuario BIGINT"
            )
            await self._execute_write(alter_usuario, target_db="novalink")
        except Exception as e:
            logging.exception(f"Error ensuring jerarquias table: {e}")

    @rx.event
    async def load_hierarchy(self):
        """Load superiors and subordinates for the selected employee."""
        self.superiores = []
        self.subalternos = []
        self.can_authorize = self.selected_employee["nivelautorizacion"] > 0
        emp_id = self.selected_employee["id"]
        if emp_id == 0:
            return
        try:
            query_sup = """
                SELECT e.id, e.nombres || ' ' || e.apellidos as name
                FROM public.jerarquias j
                JOIN public.empleados e ON j.empleado_superior = e.id
                WHERE j.empleado_subordinado = :uid
            """
            res_sup = await self._execute_query(
                query_sup, {"uid": emp_id}, target_db="novalink"
            )
            self.superiores = [
                HierarchyItem(id=row["id"], name=row["name"]) for row in res_sup
            ]
            query_sub = """
                SELECT e.id, e.nombres || ' ' || e.apellidos as name
                FROM public.jerarquias j
                JOIN public.empleados e ON j.empleado_subordinado = e.id
                WHERE j.empleado_superior = :uid
            """
            res_sub = await self._execute_query(
                query_sub, {"uid": emp_id}, target_db="novalink"
            )
            self.subalternos = [
                HierarchyItem(id=row["id"], name=row["name"]) for row in res_sub
            ]
        except Exception as e:
            logging.exception(f"Error loading hierarchy: {e}")

    @rx.event
    async def save_hierarchy(self, emp_id: int):
        """Save the current hierarchy state to the database."""
        if not self.has_db_connection or emp_id == 0:
            return
        from app.states.base_state import BaseState

        base_state = await self.get_state(BaseState)
        user_id = base_state.logged_user_id or 1
        try:
            await self._execute_write(
                "DELETE FROM public.jerarquias WHERE empleado_subordinado = :uid",
                {"uid": emp_id},
                target_db="novalink",
            )
            await self._execute_write(
                "DELETE FROM public.jerarquias WHERE empleado_superior = :uid",
                {"uid": emp_id},
                target_db="novalink",
            )
            for sup in self.superiores:
                await self._execute_write(
                    """
                    INSERT INTO public.jerarquias (empleado_superior, empleado_subordinado, fechacreacion, usuario)
                    VALUES (:sup_id, :sub_id, NOW(), :uid)
                    """,
                    {"sup_id": sup["id"], "sub_id": emp_id, "uid": user_id},
                    target_db="novalink",
                )
            for sub in self.subalternos:
                await self._execute_write(
                    """
                    INSERT INTO public.jerarquias (empleado_superior, empleado_subordinado, fechacreacion, usuario)
                    VALUES (:sup_id, :sub_id, NOW(), :uid)
                    """,
                    {"sup_id": emp_id, "sub_id": sub["id"], "uid": user_id},
                    target_db="novalink",
                )
        except Exception as e:
            logging.exception(f"Error saving hierarchy: {e}")

    @rx.event
    async def load_available_employees(self):
        """Load employees for selection, excluding current and already related."""
        self.available_employees = []
        if not self.has_db_connection:
            return
        try:
            query = """
                SELECT id, cedula || ' - ' || apellidos || ' ' || nombres as name
                FROM public.empleados
                WHERE activo = true
                ORDER BY apellidos, nombres
            """
            results = await self._execute_query(query, target_db="novalink")
            current_id = self.selected_employee["id"]
            existing_ids = {current_id}
            existing_ids.update((s["id"] for s in self.superiores))
            existing_ids.update((s["id"] for s in self.subalternos))
            self.available_employees = [
                HierarchyItem(id=row["id"], name=row["name"])
                for row in results
                if row["id"] not in existing_ids
            ]
        except Exception as e:
            logging.exception(f"Error loading available employees: {e}")

    @rx.event
    async def open_hierarchy_dialog(self, dialog_type: str):
        self.hierarchy_dialog_type = dialog_type
        self.employee_to_add_id = ""
        self.hierarchy_search_query = ""
        await self.load_available_employees()
        self.show_hierarchy_dialog = True

    @rx.event
    def close_hierarchy_dialog(self):
        self.show_hierarchy_dialog = False

    @rx.event
    def set_employee_to_add(self, value: str):
        self.employee_to_add_id = value

    @rx.event
    def add_hierarchy_relation(self):
        if not self.employee_to_add_id:
            return
        emp_id = int(self.employee_to_add_id)
        emp_name = next(
            (e["name"] for e in self.available_employees if e["id"] == emp_id),
            "Unknown",
        )
        new_item = HierarchyItem(id=emp_id, name=emp_name)
        if self.hierarchy_dialog_type == "superior":
            self.superiores.append(new_item)
        else:
            self.subalternos.append(new_item)
        self.close_hierarchy_dialog()

    @rx.event
    def select_list_superior(self, emp_id: int):
        self.selected_list_superior_id = emp_id

    @rx.event
    def select_list_subordinate(self, emp_id: int):
        self.selected_list_subordinate_id = emp_id

    @rx.event
    def remove_superior(self):
        if self.selected_list_superior_id:
            self.superiores = [
                s for s in self.superiores if s["id"] != self.selected_list_superior_id
            ]
            self.selected_list_superior_id = 0

    @rx.event
    def remove_subalterno(self):
        if self.selected_list_subordinate_id:
            self.subalternos = [
                s
                for s in self.subalternos
                if s["id"] != self.selected_list_subordinate_id
            ]
            self.selected_list_subordinate_id = 0

    @rx.event
    def set_can_authorize(self, checked: bool):
        self.can_authorize = checked
        if not checked:
            self.selected_employee["nivelautorizacion"] = 0
        elif self.selected_employee["nivelautorizacion"] == 0:
            self.selected_employee["nivelautorizacion"] = 1

    @rx.event
    def set_nivel_autorizacion(self, value: str):
        try:
            self.selected_employee["nivelautorizacion"] = int(value)
        except ValueError as e:
            logging.exception(f"Error converting nivelautorizacion to int: {e}")

    @rx.event
    async def load_config(self):
        if not self.has_db_connection:
            return
        try:
            query = "SELECT codigo, valor FROM public.parametros WHERE codigo IN (4, 5, 8, 11, 14, 17, 35, 36, 39, 40)"
            results = await self._execute_query(query, target_db="novalink")
            params = {row["codigo"]: row["valor"] for row in results}
            self.niveles_habilitados = int(params.get(4, "5"))
            self.labels_niveles = {
                "1": params.get(5, "Nivel 1"),
                "2": params.get(8, "Nivel 2"),
                "3": params.get(11, "Nivel 3"),
                "4": params.get(14, "Nivel 4"),
                "5": params.get(17, "Nivel 5"),
            }
            self.has_attr_tabular = params.get(35, "0") == "1"
            self.label_attr_tabular = params.get(36, "Atributo Tabular")
            self.has_attr_texto = params.get(39, "0") == "1"
            self.label_attr_texto = params.get(40, "Atributo Texto")
        except Exception as e:
            logging.exception(f"Error loading config: {e}")

    async def _fetch_catalog(self, table: str) -> list[CatalogItem]:
        try:
            query = f"SELECT codigo, descripcion FROM public.{table} WHERE codigo > 0 AND activo = true ORDER BY descripcion"
            results = await self._execute_query(query, target_db="novalink")
            return [
                CatalogItem(id=row["codigo"], descripcion=row["descripcion"])
                for row in results
            ]
        except Exception as e:
            logging.exception(f"Error fetching catalog {table}: {e}")
            return []

    @rx.event
    async def load_catalogs(self):
        self.cat_nivel1 = await self._fetch_catalog("niveladm1")
        self.cat_nivel2 = await self._fetch_catalog("niveladm2")
        self.cat_nivel3 = await self._fetch_catalog("niveladm3")
        self.cat_nivel4 = await self._fetch_catalog("niveladm4")
        self.cat_nivel5 = await self._fetch_catalog("niveladm5")
        self.cat_cargos = await self._fetch_catalog("cargos")
        self.cat_grupos = await self._fetch_catalog("grupos")
        self.cat_tipos = await self._fetch_catalog("tipoempleado")
        self.cat_attr_tabular = await self._fetch_catalog("atributotabularemp")

    @rx.event
    async def load_employees(self):
        try:
            query = """
                SELECT 
                    id, cedula, nombres, apellidos, correoelectronico,
                    transporte, alimentacion, zona,
                    COALESCE(to_char(fechacalculovacaciones, 'YYYY-MM-DD'), '') as fechacalculovacaciones,
                    COALESCE(to_char(fechaingreso, 'YYYY-MM-DD'), '') as fechaingreso,
                    ganarecargonocturno, ganasobretiempo, stconautorizacion,
                    ganarecargodialibre, offline,
                    niveladm1, niveladm2, niveladm3, niveladm4, niveladm5,
                    cargo, tipo, grupo, atributotabular, atributotexto,
                    accesoweb, pwd, activo,
                    COALESCE(nivelautorizacion, 0) as nivelautorizacion,
                    COALESCE(to_char(fechacreacion, 'YYYY-MM-DD HH24:MI:SS'), '') as fechacreacion,
                    COALESCE(to_char(fechamodificacion, 'YYYY-MM-DD HH24:MI:SS'), '') as fechamodificacion
                FROM public.empleados
                ORDER BY apellidos, nombres
            """
            results = await self._execute_query(query, target_db="novalink")
            self.employees = [
                Employee(
                    id=row["id"],
                    cedula=row["cedula"] or "",
                    nombres=row["nombres"] or "",
                    apellidos=row["apellidos"] or "",
                    correoelectronico=row["correoelectronico"] or "",
                    transporte=bool(row.get("transporte", False)),
                    alimentacion=bool(row.get("alimentacion", False)),
                    zona=row.get("zona") or 0,
                    fechacalculovacaciones=row["fechacalculovacaciones"],
                    fechaingreso=row["fechaingreso"],
                    ganarecargonocturno=bool(row["ganarecargonocturno"]),
                    ganasobretiempo=bool(row["ganasobretiempo"]),
                    stconautorizacion=bool(row["stconautorizacion"]),
                    ganarecargodialibre=bool(row["ganarecargodialibre"]),
                    offline=bool(row["offline"]),
                    niveladm1=row["niveladm1"] or 0,
                    niveladm2=row["niveladm2"] or 0,
                    niveladm3=row["niveladm3"] or 0,
                    niveladm4=row["niveladm4"] or 0,
                    niveladm5=row["niveladm5"] or 0,
                    cargo=row["cargo"] or 0,
                    tipo=row["tipo"] or 0,
                    grupo=row["grupo"] or 0,
                    atributotabular=row["atributotabular"] or 0,
                    atributotexto=row["atributotexto"] or "",
                    accesoweb=bool(row["accesoweb"]),
                    pwd=row["pwd"] or "",
                    activo=bool(row["activo"]),
                    nivelautorizacion=row.get("nivelautorizacion") or 0,
                    fechacreacion=row["fechacreacion"],
                    fechamodificacion=row["fechamodificacion"],
                )
                for row in results
            ]
        except Exception as e:
            logging.exception(f"Error loading employees: {e}")
            self.employees = []

    @rx.event
    async def save_employee(self):
        emp = self.selected_employee
        if not self.can_authorize:
            emp["nivelautorizacion"] = 0
        elif emp["nivelautorizacion"] == 0:
            emp["nivelautorizacion"] = 1
        emp["nombres"] = emp["nombres"].strip().upper()
        emp["apellidos"] = emp["apellidos"].strip().upper()
        validation_errors = []
        if not emp["cedula"] or not emp["cedula"].strip():
            validation_errors.append("La Cédula es obligatoria")
        if not emp["nombres"] or not emp["nombres"].strip():
            validation_errors.append("Los Nombres son obligatorios")
        if not emp["apellidos"] or not emp["apellidos"].strip():
            validation_errors.append("Los Apellidos son obligatorios")
        if emp["niveladm1"] <= 0:
            label = self.labels_niveles.get("1", "Nivel 1")
            validation_errors.append(f"El campo '{label}' es obligatorio")
        if self.niveles_habilitados >= 2 and emp["niveladm2"] <= 0:
            label = self.labels_niveles.get("2", "Nivel 2")
            validation_errors.append(f"El campo '{label}' es obligatorio")
        if self.niveles_habilitados >= 3 and emp["niveladm3"] <= 0:
            label = self.labels_niveles.get("3", "Nivel 3")
            validation_errors.append(f"El campo '{label}' es obligatorio")
        if self.niveles_habilitados >= 4 and emp["niveladm4"] <= 0:
            label = self.labels_niveles.get("4", "Nivel 4")
            validation_errors.append(f"El campo '{label}' es obligatorio")
        if self.niveles_habilitados >= 5 and emp["niveladm5"] <= 0:
            label = self.labels_niveles.get("5", "Nivel 5")
            validation_errors.append(f"El campo '{label}' es obligatorio")
        if emp["cargo"] <= 0:
            validation_errors.append("El Cargo es obligatorio")
        if emp["tipo"] <= 0:
            validation_errors.append("El Tipo de Empleado es obligatorio")
        if emp.get("grupo", 0) <= 0:
            validation_errors.append("El Grupo es obligatorio")
        if validation_errors:
            yield rx.toast.error(
                f"Error de validación: {', '.join(validation_errors)}."
            )
            return
        from app.states.base_state import BaseState

        base_state = await self.get_state(BaseState)
        user_id = base_state.logged_user_id or 1
        pwd_val = emp["pwd"]
        if len(pwd_val) != 64:
            pwd_val = hashlib.sha256(pwd_val.encode()).hexdigest()
        try:
            new_id = 0
            if self.id_input:
                new_id = int(self.id_input)
            if self.editing_employee_id == 0:
                if new_id == 0:
                    next_id_res = await self._execute_query(
                        "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM public.empleados",
                        target_db="novalink",
                    )
                    new_id = next_id_res[0]["next_id"] if next_id_res else 1
                else:
                    check_query = "SELECT 1 FROM public.empleados WHERE id = :id"
                    exists_res = await self._execute_query(
                        check_query, {"id": new_id}, target_db="novalink"
                    )
                    if exists_res:
                        yield rx.toast.error(
                            f"El ID {new_id} ya existe. Por favor use otro."
                        )
                        return
                query = """
                    INSERT INTO public.empleados (
                        id, cedula, nombres, apellidos, correoelectronico,
                        transporte, alimentacion, zona, fechacalculovacaciones, fechaingreso,
                        ganarecargonocturno, ganasobretiempo, stconautorizacion, ganarecargodialibre, offline,
                        niveladm1, niveladm2, niveladm3, niveladm4, niveladm5,
                        cargo, tipo, grupo, atributotabular, atributotexto,
                        accesoweb, pwd, activo, fechacreacion, usuariocrea, usuario, nivelautorizacion)
                    VALUES (
                        :id, :cedula, :nombres, :apellidos, :email,
                        :transporte, :alimentacion, :zona, 
                        COALESCE(NULLIF(:f_vac, '')::date, CURRENT_DATE), 
                        COALESCE(NULLIF(:f_ing, '')::date, CURRENT_DATE),
                        :grn, :gst, :ast, :rel, :app,
                        :n1, :n2, :n3, :n4, :n5,
                        :cc, :cte, :grp, :cat, :atxt,
                        :web, :pwd, :activo, NOW(), :uid, :uid, :nauth
                    )
                """
                params = {
                    "id": new_id,
                    "cedula": emp["cedula"],
                    "nombres": emp["nombres"],
                    "apellidos": emp["apellidos"],
                    "email": emp["correoelectronico"],
                    "transporte": emp.get("transporte", False),
                    "alimentacion": emp.get("alimentacion", False),
                    "zona": emp.get("zona", 0),
                    "f_vac": emp.get("fechacalculovacaciones", ""),
                    "f_ing": emp.get("fechaingreso", ""),
                    "grn": emp["ganarecargonocturno"],
                    "gst": emp["ganasobretiempo"],
                    "ast": emp["stconautorizacion"],
                    "rel": emp["ganarecargodialibre"],
                    "app": emp["offline"],
                    "n1": emp["niveladm1"],
                    "n2": emp["niveladm2"],
                    "n3": emp["niveladm3"],
                    "n4": emp["niveladm4"],
                    "n5": emp["niveladm5"],
                    "cc": emp["cargo"],
                    "cte": emp["tipo"],
                    "grp": emp.get("grupo", 0),
                    "cat": emp["atributotabular"],
                    "atxt": emp["atributotexto"],
                    "web": emp["accesoweb"],
                    "pwd": pwd_val,
                    "activo": emp["activo"],
                    "uid": user_id,
                    "nauth": emp.get("nivelautorizacion") or 0,
                }
                await self._execute_write(query, params, target_db="novalink")
                self.editing_employee_id = new_id
                self.selected_employee["id"] = new_id
                yield rx.toast.success(f"Empleado creado con ID {new_id}")
            else:
                original_id = self.editing_employee_id
                if new_id == 0:
                    new_id = original_id
                if new_id != original_id:
                    check_query = "SELECT 1 FROM public.empleados WHERE id = :id AND id != :old_id"
                    exists_res = await self._execute_query(
                        check_query,
                        {"id": new_id, "old_id": original_id},
                        target_db="novalink",
                    )
                    if exists_res:
                        yield rx.toast.error(
                            f"El ID {new_id} ya está en uso por otro empleado."
                        )
                        return
                query = """
                    UPDATE public.empleados SET
                        id = :new_id,
                        cedula = :cedula, nombres = :nombres, apellidos = :apellidos, correoelectronico = :email,
                        transporte = :transporte, alimentacion = :alimentacion, zona = :zona, 
                        fechacalculovacaciones = COALESCE(NULLIF(:f_vac, '')::date, CURRENT_DATE), 
                        fechaingreso = COALESCE(NULLIF(:f_ing, '')::date, CURRENT_DATE),
                        ganarecargonocturno = :grn, ganasobretiempo = :gst, stconautorizacion = :ast, ganarecargodialibre = :rel, offline = :app,
                        niveladm1 = :n1, niveladm2 = :n2, niveladm3 = :n3, niveladm4 = :n4, niveladm5 = :n5,
                        cargo = :cc, tipo = :cte, grupo = :grp, atributotabular = :cat, atributotexto = :atxt,
                        accesoweb = :web, pwd = :pwd, activo = :activo, fechamodificacion = NOW(), usuariomodifica = :uid,
                        nivelautorizacion = :nauth
                    WHERE id = :old_id
                """
                params = {
                    "new_id": new_id,
                    "old_id": original_id,
                    "cedula": emp["cedula"],
                    "nombres": emp["nombres"],
                    "apellidos": emp["apellidos"],
                    "email": emp["correoelectronico"],
                    "transporte": emp.get("transporte", False),
                    "alimentacion": emp.get("alimentacion", False),
                    "zona": emp.get("zona", 0),
                    "f_vac": emp.get("fechacalculovacaciones", ""),
                    "f_ing": emp.get("fechaingreso", ""),
                    "grn": emp["ganarecargonocturno"],
                    "gst": emp["ganasobretiempo"],
                    "ast": emp["stconautorizacion"],
                    "rel": emp["ganarecargodialibre"],
                    "app": emp["offline"],
                    "n1": emp["niveladm1"],
                    "n2": emp["niveladm2"],
                    "n3": emp["niveladm3"],
                    "n4": emp["niveladm4"],
                    "n5": emp["niveladm5"],
                    "cc": emp["cargo"],
                    "cte": emp["tipo"],
                    "grp": emp.get("grupo", 0),
                    "cat": emp["atributotabular"],
                    "atxt": emp["atributotexto"],
                    "web": emp["accesoweb"],
                    "pwd": pwd_val,
                    "activo": emp["activo"],
                    "uid": user_id,
                    "nauth": emp.get("nivelautorizacion") or 0,
                }
                await self._execute_write(query, params, target_db="novalink")
                if new_id != original_id:
                    self.editing_employee_id = new_id
                    self.selected_employee["id"] = new_id
                yield rx.toast.success("Empleado actualizado correctamente")
            await self.save_hierarchy(new_id)
            await self.load_employees()
        except Exception as e:
            logging.exception(f"Error saving employee: {e}")
            yield rx.toast.error(f"Error al guardar: {e}")