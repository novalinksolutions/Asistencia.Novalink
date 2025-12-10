import reflex as rx
from app.states.empleados_state import EmpleadosState, Employee


def employee_list_item(emp: Employee) -> rx.Component:
    is_selected = EmpleadosState.selected_employee["id"] == emp["id"]
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                f"{emp['apellidos']} {emp['nombres']}",
                class_name="font-medium text-xs text-gray-900 truncate",
            ),
            rx.el.div(
                rx.icon("id-card", class_name="w-3 h-3 text-gray-400 mr-1"),
                rx.el.span(emp["cedula"], class_name="text-[10px] text-gray-500"),
                class_name="flex items-center mt-0.5",
            ),
        ),
        on_click=lambda: EmpleadosState.select_employee(emp),
        class_name=rx.cond(
            is_selected,
            "p-2 rounded-lg bg-blue-50 border border-blue-200 cursor-pointer transition-all hover:shadow-sm",
            rx.cond(
                emp["activo"],
                "p-2 rounded-lg hover:bg-gray-50 cursor-pointer border border-transparent transition-all",
                "p-2 rounded-lg bg-gray-50 opacity-60 cursor-pointer border border-transparent transition-all grayscale",
            ),
        ),
    )


def form_input(
    label: str,
    field: str,
    type_: str = "text",
    placeholder: str = "",
    read_only: bool = False,
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label,
            class_name="block text-[10px] font-medium text-gray-500 uppercase tracking-wider mb-0.5",
        ),
        rx.el.input(
            type=type_,
            default_value=EmpleadosState.selected_employee[field].to(str),
            read_only=read_only,
            placeholder=placeholder,
            on_change=lambda v: EmpleadosState.set_field(field, v),
            class_name=rx.cond(
                read_only,
                "w-full px-2.5 py-1.5 bg-gray-100 border border-gray-200 rounded-md text-gray-500 cursor-not-allowed text-xs",
                "w-full px-2.5 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white text-xs",
            ),
        ),
        class_name="w-full",
    )


def form_checkbox(label: str, field: str) -> rx.Component:
    return rx.el.label(
        rx.el.input(
            type="checkbox",
            checked=EmpleadosState.selected_employee[field],
            on_change=lambda v: EmpleadosState.toggle_bool_field(field, v),
            class_name="w-3.5 h-3.5 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
        ),
        rx.el.span(label, class_name="ml-2 text-xs text-gray-700"),
        class_name="flex items-center p-1.5 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer",
    )


def form_select(
    label: str, field: str, options: list[dict], placeholder: str = "Seleccione..."
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label,
            class_name="block text-[10px] font-medium text-gray-500 uppercase tracking-wider mb-0.5",
        ),
        rx.el.select(
            rx.el.option(placeholder, value="0"),
            rx.foreach(
                options,
                lambda opt: rx.el.option(opt["descripcion"], value=opt["id"].to(str)),
            ),
            value=EmpleadosState.selected_employee[field].to(str),
            on_change=lambda v: EmpleadosState.set_int_field(field, v),
            class_name="w-full px-2.5 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white text-xs",
        ),
        class_name="w-full",
    )


def tab_datos_basicos() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "ID Sistema",
                    class_name="block text-[10px] font-medium text-gray-500 uppercase tracking-wider mb-0.5",
                ),
                rx.el.input(
                    type="text",
                    on_change=EmpleadosState.set_id_field,
                    placeholder="Id principal",
                    class_name="w-full px-2.5 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white font-mono text-xs",
                    default_value=EmpleadosState.id_input,
                ),
                class_name="w-full",
            ),
            form_input("Cédula", "cedula", placeholder="Cédula"),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-3 mb-2",
        ),
        rx.el.div(
            form_input("Nombres", "nombres", placeholder="Nombres completos"),
            form_input("Apellidos", "apellidos", placeholder="Apellidos completos"),
            class_name="grid grid-cols-2 gap-3 mb-2",
        ),
        rx.el.div(
            rx.el.label(
                "Correo Electrónico",
                class_name="block text-[10px] font-medium text-gray-500 uppercase tracking-wider mb-0.5",
            ),
            rx.el.div(
                rx.el.input(
                    type="text",
                    read_only=~EmpleadosState.is_email_editable,
                    on_change=lambda v: EmpleadosState.set_field(
                        "correoelectronico", v
                    ),
                    placeholder="ejemplo@correo.com",
                    class_name=rx.cond(
                        ~EmpleadosState.is_email_editable,
                        "w-full px-2.5 py-1.5 bg-gray-50 border border-gray-200 rounded-md text-gray-500 font-mono text-xs",
                        "w-full px-2.5 py-1.5 border border-blue-300 bg-white rounded-md focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-gray-900 text-xs",
                    ),
                    default_value=rx.cond(
                        EmpleadosState.is_email_editable,
                        EmpleadosState.selected_employee["correoelectronico"],
                        EmpleadosState.masked_email,
                    ),
                ),
                rx.cond(
                    EmpleadosState.selected_employee["id"] != 0,
                    rx.el.button(
                        rx.cond(
                            EmpleadosState.is_email_editable,
                            rx.icon("eye-off", class_name="h-3 w-3 text-gray-500"),
                            rx.icon("pencil", class_name="h-3 w-3 text-blue-600"),
                        ),
                        on_click=EmpleadosState.toggle_email_editable,
                        class_name="absolute right-2 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 rounded-md transition-colors",
                        title=rx.cond(
                            EmpleadosState.is_email_editable,
                            "Ocultar email",
                            "Editar email",
                        ),
                    ),
                    None,
                ),
                class_name="relative",
            ),
            rx.cond(
                ~EmpleadosState.is_email_editable,
                rx.el.p(
                    rx.icon("shield-check", class_name="inline h-3 w-3 mr-1"),
                    "Email enmascarado por seguridad",
                    class_name="text-[10px] text-gray-400 mt-0.5 flex items-center",
                ),
                None,
            ),
            class_name="w-full mb-2",
        ),
        rx.el.div(
            rx.el.h4(
                "Configuración de Nómina y Asistencia",
                class_name="text-xs font-semibold text-gray-900 mt-2 mb-2",
            ),
            rx.el.div(
                form_checkbox("Gana recargo nocturno", "ganarecargonocturno"),
                form_checkbox("Gana sobretiempo", "ganasobretiempo"),
                form_checkbox(
                    "El sobretiempo necesita ser autorizado", "stconautorizacion"
                ),
                form_checkbox(
                    "Aplica recargo ext. si trabaja en días libres",
                    "ganarecargodialibre",
                ),
                form_checkbox("Aplicación Móvil (Offline)", "offline"),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-1",
            ),
            class_name="bg-gray-50 p-3 rounded-lg border border-gray-100 mt-2",
        ),
        class_name="flex flex-col",
    )


def tab_organizacional() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h4(
                "Niveles Administrativos",
                class_name="text-xs font-semibold text-gray-900 mb-2",
            ),
            rx.el.div(
                rx.cond(
                    EmpleadosState.niveles_habilitados >= 1,
                    form_select(
                        EmpleadosState.labels_niveles["1"],
                        "niveladm1",
                        EmpleadosState.cat_nivel1,
                    ),
                ),
                rx.cond(
                    EmpleadosState.niveles_habilitados >= 2,
                    form_select(
                        EmpleadosState.labels_niveles["2"],
                        "niveladm2",
                        EmpleadosState.cat_nivel2,
                    ),
                ),
                rx.cond(
                    EmpleadosState.niveles_habilitados >= 3,
                    form_select(
                        EmpleadosState.labels_niveles["3"],
                        "niveladm3",
                        EmpleadosState.cat_nivel3,
                    ),
                ),
                rx.cond(
                    EmpleadosState.niveles_habilitados >= 4,
                    form_select(
                        EmpleadosState.labels_niveles["4"],
                        "niveladm4",
                        EmpleadosState.cat_nivel4,
                    ),
                ),
                rx.cond(
                    EmpleadosState.niveles_habilitados >= 5,
                    form_select(
                        EmpleadosState.labels_niveles["5"],
                        "niveladm5",
                        EmpleadosState.cat_nivel5,
                    ),
                ),
                class_name="grid grid-cols-1 md:grid-cols-3 gap-3",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.h4(
                "Clasificación y Atributos",
                class_name="text-xs font-semibold text-gray-900 mb-2",
            ),
            rx.el.div(
                form_select("Cargo", "cargo", EmpleadosState.cat_cargos),
                form_select("Tipo de Empleado", "tipo", EmpleadosState.cat_tipos),
                form_select("Grupo", "grupo", EmpleadosState.cat_grupos),
                rx.cond(
                    EmpleadosState.has_attr_tabular,
                    form_select(
                        EmpleadosState.label_attr_tabular,
                        "atributotabular",
                        EmpleadosState.cat_attr_tabular,
                    ),
                ),
                rx.cond(
                    EmpleadosState.has_attr_texto,
                    form_input(EmpleadosState.label_attr_texto, "atributotexto"),
                ),
                class_name="grid grid-cols-1 md:grid-cols-3 gap-3",
            ),
            class_name="",
        ),
        class_name="flex flex-col",
    )


def tab_permisos() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("shield-check", class_name="w-6 h-6 text-blue-600 mb-2"),
            rx.el.h3(
                "Acceso al Portal de Empleados",
                class_name="text-base font-medium text-gray-900",
            ),
            rx.el.p(
                "Configure si este empleado puede iniciar sesión en la plataforma web para revisar sus roles de pago y asistencia.",
                class_name="text-xs text-gray-500 mt-1 mb-4 max-w-lg",
            ),
            rx.el.div(
                rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        checked=EmpleadosState.selected_employee["accesoweb"],
                        on_change=lambda v: EmpleadosState.toggle_bool_field(
                            "accesoweb", v
                        ),
                        class_name="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
                    ),
                    rx.el.span(
                        "Habilitar acceso a interfaz web",
                        class_name="ml-2 text-xs font-medium text-gray-900",
                    ),
                    class_name="flex items-center p-3 bg-white border border-gray-200 rounded-lg shadow-sm cursor-pointer hover:border-blue-300 transition-all",
                ),
                class_name="mb-4",
            ),
            rx.cond(
                EmpleadosState.is_pwd_enabled,
                rx.el.div(
                    rx.el.label(
                        "Contraseña de acceso",
                        class_name="block text-[10px] font-medium text-gray-500 uppercase tracking-wider mb-0.5",
                    ),
                    rx.el.div(
                        rx.icon(
                            "lock",
                            class_name="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400",
                        ),
                        rx.el.input(
                            type="text",
                            default_value=EmpleadosState.selected_employee["pwd"],
                            on_change=lambda v: EmpleadosState.set_field("pwd", v),
                            class_name="w-full pl-8 pr-4 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all font-mono text-xs",
                        ),
                        class_name="relative max-w-xs",
                    ),
                    rx.el.p(
                        "La contraseña por defecto es '12345678'. Se recomienda cambiarla en el primer inicio de sesión.",
                        class_name="text-[10px] text-amber-600 mt-1 flex items-center gap-1",
                    ),
                    class_name="animate-in fade-in slide-in-from-top-2 duration-300",
                ),
            ),
            class_name="flex flex-col items-start",
        ),
        class_name="p-4 bg-gray-50/50 rounded-lg border border-gray-100 h-full",
    )


def form_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                EmpleadosState.form_title, class_name="text-lg font-bold text-gray-900"
            ),
            rx.el.div(
                rx.el.button(
                    "Cancelar",
                    on_click=EmpleadosState.cancel_edit,
                    class_name="px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors",
                ),
                rx.el.button(
                    rx.icon("save", class_name="w-3.5 h-3.5 mr-1.5"),
                    "Guardar",
                    on_click=EmpleadosState.save_employee,
                    class_name="flex items-center px-3 py-1.5 text-xs font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm",
                ),
                class_name="flex gap-2",
            ),
            class_name="flex justify-between items-center mb-3 pb-3 border-b",
        ),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger(
                    "Datos Básicos",
                    value="tab1",
                    class_name="px-3 py-1.5 text-xs font-medium text-gray-600 border-b-2 border-transparent hover:text-gray-800 data-[state=active]:border-blue-600 data-[state=active]:text-blue-600 transition-all",
                ),
                rx.tabs.trigger(
                    "Datos Organizacionales",
                    value="tab2",
                    class_name="px-3 py-1.5 text-xs font-medium text-gray-600 border-b-2 border-transparent hover:text-gray-800 data-[state=active]:border-blue-600 data-[state=active]:text-blue-600 transition-all",
                ),
                rx.tabs.trigger(
                    "Permisos",
                    value="tab3",
                    class_name="px-3 py-1.5 text-xs font-medium text-gray-600 border-b-2 border-transparent hover:text-gray-800 data-[state=active]:border-blue-600 data-[state=active]:text-blue-600 transition-all",
                ),
                class_name="flex gap-2 mb-3 border-b border-gray-100",
            ),
            rx.tabs.content(
                tab_datos_basicos(),
                value="tab1",
                class_name="outline-none animate-in fade-in duration-300",
            ),
            rx.tabs.content(
                tab_organizacional(),
                value="tab2",
                class_name="outline-none animate-in fade-in duration-300",
            ),
            rx.tabs.content(
                tab_permisos(),
                value="tab3",
                class_name="outline-none animate-in fade-in duration-300",
            ),
            default_value="tab1",
            class_name="flex-1 overflow-y-auto custom-scrollbar pr-1",
        ),
        rx.el.div(
            rx.el.label(
                rx.el.input(
                    type="checkbox",
                    checked=EmpleadosState.selected_employee["activo"],
                    on_change=lambda v: EmpleadosState.toggle_bool_field("activo", v),
                    class_name="w-3.5 h-3.5 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
                ),
                rx.el.span(
                    "Empleado Activo",
                    class_name="ml-2 text-xs font-medium text-gray-900",
                ),
                class_name="flex items-center",
            ),
            class_name="mt-3 pt-3 border-t border-gray-100",
        ),
        class_name="bg-white p-4 rounded-xl shadow-sm border h-full flex flex-col",
        key=EmpleadosState.editing_employee_id,
    )


def empleados_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Gestión de Empleados",
                class_name="text-xl font-bold text-gray-900 tracking-tight",
            ),
            class_name="mb-3",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "search",
                            class_name="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400",
                        ),
                        rx.el.input(
                            placeholder="Buscar por nombre o cédula...",
                            on_change=EmpleadosState.set_search_query,
                            class_name="w-full pl-8 pr-3 py-1.5 rounded-lg border border-gray-200 bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-xs",
                        ),
                        class_name="relative mb-2",
                    ),
                    rx.el.div(
                        rx.el.label(
                            rx.el.input(
                                type="checkbox",
                                checked=EmpleadosState.show_inactive,
                                on_change=EmpleadosState.set_show_inactive,
                                class_name="w-3 h-3 rounded border-gray-300 text-blue-600 focus:ring-blue-500",
                            ),
                            rx.el.span(
                                "Mostrar inactivos",
                                class_name="ml-1.5 text-[10px] font-medium text-gray-600",
                            ),
                            class_name="flex items-center cursor-pointer select-none",
                        ),
                        rx.el.button(
                            rx.icon("plus", class_name="w-3 h-3 mr-1"),
                            "Nuevo",
                            on_click=EmpleadosState.new_employee,
                            class_name="flex items-center px-2.5 py-1 bg-blue-600 text-white text-[10px] font-medium rounded hover:bg-blue-700 transition-all",
                        ),
                        class_name="flex justify-between items-center mb-2",
                    ),
                    rx.cond(
                        EmpleadosState.search_query.length() < 3,
                        rx.el.div(
                            rx.icon("clock", class_name="w-3 h-3 mr-1"),
                            "Últimos 10 modificados (7 días)",
                            class_name="flex items-center text-[10px] text-gray-400 font-medium mb-1 pl-1 uppercase tracking-wider",
                        ),
                        None,
                    ),
                    rx.el.div(
                        rx.foreach(
                            EmpleadosState.filtered_employees, employee_list_item
                        ),
                        class_name="space-y-1 overflow-y-auto pr-1 custom-scrollbar flex-1",
                    ),
                    class_name="flex flex-col h-full",
                ),
                class_name="w-full md:w-[280px] bg-white p-3 rounded-xl border border-gray-200 h-[calc(100vh-8rem)] shadow-sm shrink-0",
            ),
            rx.el.div(
                rx.cond(
                    EmpleadosState.is_editing,
                    form_section(),
                    rx.el.div(
                        rx.icon(
                            "user-round-search",
                            class_name="w-12 h-12 text-gray-200 mb-3",
                        ),
                        rx.el.h3(
                            "Seleccione un empleado",
                            class_name="text-base font-medium text-gray-900 mb-1",
                        ),
                        rx.el.p(
                            "Seleccione un registro de la lista o cree uno nuevo para comenzar.",
                            class_name="text-gray-500 text-center max-w-xs text-xs",
                        ),
                        class_name="h-full flex flex-col items-center justify-center bg-gray-50/50 rounded-xl border-2 border-dashed border-gray-200",
                    ),
                ),
                class_name="flex-1 h-[calc(100vh-8rem)] min-w-0",
            ),
            class_name="flex flex-col md:flex-row gap-3",
        ),
        class_name="animate-fade-in-up h-full",
        on_mount=EmpleadosState.on_load,
    )