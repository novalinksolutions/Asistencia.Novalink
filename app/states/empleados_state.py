import reflex as rx
from typing import TypedDict, Any, Optional
import logging
import hashlib
from app.states.database_state import DatabaseState


class Employee(TypedDict):
    id: int
    cedula: str
    codigoalterno: str
    nombres: str
    apellidos: str
    correoelectronico: str
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
    atributotabular: int
    atributotexto: str
    accesoweb: bool
    pwd: str
    activo: bool


class CatalogItem(TypedDict):
    id: int
    descripcion: str


class EmpleadosState(DatabaseState):
    employees: list[Employee] = []
    selected_employee: Employee = {
        "id": 0,
        "cedula": "",
        "codigoalterno": "",
        "nombres": "",
        "apellidos": "",
        "correoelectronico": "",
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
        "atributotabular": 0,
        "atributotexto": "",
        "accesoweb": False,
        "pwd": "12345678",
        "activo": True,
    }
    cat_nivel1: list[CatalogItem] = []
    cat_nivel2: list[CatalogItem] = []
    cat_nivel3: list[CatalogItem] = []
    cat_nivel4: list[CatalogItem] = []
    cat_nivel5: list[CatalogItem] = []
    cat_cargos: list[CatalogItem] = []
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
    def filtered_employees(self) -> list[Employee]:
        items = self.employees
        if not self.show_inactive:
            items = [e for e in items if e["activo"]]
        if self.search_query:
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
        self.selected_employee = {
            "id": 0,
            "cedula": "",
            "codigoalterno": "",
            "nombres": "",
            "apellidos": "",
            "correoelectronico": "",
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
            "atributotabular": 0,
            "atributotexto": "",
            "accesoweb": False,
            "pwd": "12345678",
            "activo": True,
        }
        self.is_email_editable = True
        self.is_editing = True

    @rx.event
    def select_employee(self, employee: Employee):
        self.editing_employee_id = employee["id"]
        self.selected_employee = employee.copy()
        self.id_input = f"{employee['id']:010d}"
        self.is_editing = True
        self.is_email_editable = False

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
                    codigoalterno VARCHAR(20) DEFAULT '',
                    apellidos VARCHAR(50),
                    nombres VARCHAR(50),
                    correoelectronico VARCHAR(50),
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
                    atributotabular BIGINT DEFAULT 0,
                    atributotexto VARCHAR(10),
                    accesoweb BOOLEAN DEFAULT false,
                    pwd TEXT,
                    activo BOOLEAN DEFAULT true,
                    fechacreacion TIMESTAMP DEFAULT NOW(),
                    usuariocrea BIGINT,
                    fechamodificacion TIMESTAMP,
                    usuariomodifica BIGINT
                )
            """
            await self._execute_write(query, target_db="novalink")
        except Exception as e:
            logging.exception(f"Error ensuring empleados table: {e}")

    @rx.event
    async def on_load(self):
        await self._ensure_tables()
        await self.load_config()
        await self.load_catalogs()
        await self.load_employees()

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
        self.cat_tipos = await self._fetch_catalog("tipoempleado")
        self.cat_attr_tabular = await self._fetch_catalog("atributotabularemp")

    @rx.event
    async def load_employees(self):
        try:
            query = """
                SELECT 
                    id, cedula, codigoalterno, nombres, apellidos, correoelectronico,
                    ganarecargonocturno, ganasobretiempo, stconautorizacion,
                    ganarecargodialibre, offline,
                    niveladm1, niveladm2, niveladm3, niveladm4, niveladm5,
                    cargo, tipo, atributotabular, atributotexto,
                    accesoweb, pwd, activo
                FROM public.empleados
                ORDER BY apellidos, nombres
            """
            results = await self._execute_query(query, target_db="novalink")
            self.employees = [
                Employee(
                    id=row["id"],
                    cedula=row["cedula"] or "",
                    codigoalterno=row["codigoalterno"] or "",
                    nombres=row["nombres"] or "",
                    apellidos=row["apellidos"] or "",
                    correoelectronico=row["correoelectronico"] or "",
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
                    atributotabular=row["atributotabular"] or 0,
                    atributotexto=row["atributotexto"] or "",
                    accesoweb=bool(row["accesoweb"]),
                    pwd=row["pwd"] or "",
                    activo=bool(row["activo"]),
                )
                for row in results
            ]
        except Exception as e:
            logging.exception(f"Error loading employees: {e}")
            self.employees = []

    @rx.event
    async def save_employee(self):
        emp = self.selected_employee
        if not self.id_input:
            return rx.toast.error("El ID es obligatorio y debe ser numérico.")
        if not emp["nombres"] or not emp["apellidos"] or (not emp["cedula"]):
            return rx.toast.error("Nombres, Apellidos y Cédula son obligatorios.")
        from app.states.base_state import BaseState

        base_state = await self.get_state(BaseState)
        user_id = base_state.logged_user_id or 1
        pwd_val = emp["pwd"]
        if len(pwd_val) != 64:
            pwd_val = hashlib.sha256(pwd_val.encode()).hexdigest()
        try:
            new_id = int(self.id_input)
            if self.editing_employee_id == 0:
                check_query = "SELECT 1 FROM public.empleados WHERE id = :id"
                exists_res = await self._execute_query(
                    check_query, {"id": new_id}, target_db="novalink"
                )
                if exists_res:
                    return rx.toast.error(
                        f"El ID {new_id} ya existe. Por favor use otro."
                    )
                query = """
                    INSERT INTO public.empleados (
                        id, cedula, codigoalterno, nombres, apellidos, correoelectronico,
                        ganarecargonocturno, ganasobretiempo, stconautorizacion, ganarecargodialibre, offline,
                        niveladm1, niveladm2, niveladm3, niveladm4, niveladm5,
                        cargo, tipo, atributotabular, atributotexto,
                        accesoweb, pwd, activo, fechacreacion, usuariocrea)
                    VALUES (
                        :id, :cedula, :cod_alt, :nombres, :apellidos, :email,
                        :grn, :gst, :ast, :rel, :app,
                        :n1, :n2, :n3, :n4, :n5,
                        :cc, :cte, :cat, :atxt,
                        :web, :pwd, :activo, NOW(), :uid
                    )
                """
                params = {
                    "id": new_id,
                    "cedula": emp["cedula"],
                    "cod_alt": emp.get("codigoalterno", ""),
                    "nombres": emp["nombres"],
                    "apellidos": emp["apellidos"],
                    "email": emp["correoelectronico"],
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
                    "cat": emp["atributotabular"],
                    "atxt": emp["atributotexto"],
                    "web": emp["accesoweb"],
                    "pwd": pwd_val,
                    "activo": emp["activo"],
                    "uid": user_id,
                }
                await self._execute_write(query, params, target_db="novalink")
                rx.toast.success(f"Empleado creado con ID {new_id}")
            else:
                original_id = self.editing_employee_id
                if new_id != original_id:
                    check_query = "SELECT 1 FROM public.empleados WHERE id = :id AND id != :old_id"
                    exists_res = await self._execute_query(
                        check_query,
                        {"id": new_id, "old_id": original_id},
                        target_db="novalink",
                    )
                    if exists_res:
                        return rx.toast.error(
                            f"El ID {new_id} ya está en uso por otro empleado."
                        )
                query = """
                    UPDATE public.empleados SET
                        id = :new_id,
                        cedula = :cedula, codigoalterno = :cod_alt, nombres = :nombres, apellidos = :apellidos, correoelectronico = :email,
                        ganarecargonocturno = :grn, ganasobretiempo = :gst, stconautorizacion = :ast, ganarecargodialibre = :rel, offline = :app,
                        niveladm1 = :n1, niveladm2 = :n2, niveladm3 = :n3, niveladm4 = :n4, niveladm5 = :n5,
                        cargo = :cc, tipo = :cte, atributotabular = :cat, atributotexto = :atxt,
                        accesoweb = :web, pwd = :pwd, activo = :activo, fechamodificacion = NOW(), usuariomodifica = :uid
                    WHERE id = :old_id
                """
                params = {
                    "new_id": new_id,
                    "old_id": original_id,
                    "cedula": emp["cedula"],
                    "cod_alt": emp.get("codigoalterno", ""),
                    "nombres": emp["nombres"],
                    "apellidos": emp["apellidos"],
                    "email": emp["correoelectronico"],
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
                    "cat": emp["atributotabular"],
                    "atxt": emp["atributotexto"],
                    "web": emp["accesoweb"],
                    "pwd": pwd_val,
                    "activo": emp["activo"],
                    "uid": user_id,
                }
                await self._execute_write(query, params, target_db="novalink")
                rx.toast.success("Empleado actualizado correctamente")
            self.cancel_edit()
            await self.load_employees()
        except Exception as e:
            logging.exception(f"Error saving employee: {e}")
            rx.toast.error(f"Error al guardar: {e}")