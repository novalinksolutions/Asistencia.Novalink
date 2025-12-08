import reflex as rx
from app.states.empleados_state import EmpleadosState, Employee


def employee_list_item(emp: Employee) -> rx.Component:
    is_selected = EmpleadosState.selected_employee["id"] == emp["id"]
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                f"{emp['apellidos']} {emp['nombres']}",
                class_name="font-medium text-sm text-gray-900 truncate",
            ),
            rx.el.div(
                rx.icon("id-card", class_name="w-3 h-3 text-gray-400 mr-1"),
                rx.el.span(emp["cedula"], class_name="text-xs text-gray-500"),
                class_name="flex items-center mt-0.5",
            ),
        ),
        on_click=lambda: EmpleadosState.select_employee(emp),
        class_name=rx.cond(
            is_selected,
            "p-3 rounded-lg bg-blue-50 border border-blue-200 cursor-pointer transition-all hover:shadow-sm",
            rx.cond(
                emp["activo"],
                "p-3 rounded-lg hover:bg-gray-50 cursor-pointer border border-transparent transition-all",
                "p-3 rounded-lg bg-gray-50 opacity-60 cursor-pointer border border-transparent transition-all grayscale",
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
            class_name="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1",
        ),
        rx.el.input(
            type=type_,
            default_value=EmpleadosState.selected_employee[field].to(str),
            read_only=read_only,
            placeholder=placeholder,
            on_change=lambda v: EmpleadosState.set_field(field, v),
            class_name=rx.cond(
                read_only,
                "w-full px-3 py-2 bg-gray-100 border border-gray-200 rounded-lg text-gray-500 cursor-not-allowed",
                "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white",
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
            class_name="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
        ),
        rx.el.span(label, class_name="ml-2 text-sm text-gray-700"),
        class_name="flex items-center p-2 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer",
    )


def form_select(
    label: str, field: str, options: list[dict], placeholder: str = "Seleccione..."
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label,
            class_name="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1",
        ),
        rx.el.select(
            rx.el.option(placeholder, value="0"),
            rx.foreach(
                options,
                lambda opt: rx.el.option(opt["descripcion"], value=opt["id"].to(str)),
            ),
            value=EmpleadosState.selected_employee[field].to(str),
            on_change=lambda v: EmpleadosState.set_int_field(field, v),
            class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white",
        ),
        class_name="w-full",
    )


def tab_datos_basicos() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            form_input("ID", "id", read_only=True),
            form_input("Cédula", "cedula", placeholder="0000000000"),
            class_name="grid grid-cols-2 gap-4 mb-4",
        ),
        rx.el.div(
            form_input("Nombres", "nombres", placeholder="Nombres completos"),
            form_input("Apellidos", "apellidos", placeholder="Apellidos completos"),
            class_name="grid grid-cols-2 gap-4 mb-4",
        ),
        form_input(
            "Correo Electrónico",
            "correoelectronico",
            type_="email",
            placeholder="ejemplo@correo.com",
        ),
        rx.el.div(
            rx.el.h4(
                "Configuración de Nómina y Asistencia",
                class_name="text-sm font-semibold text-gray-900 mt-6 mb-3",
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
                class_name="grid grid-cols-1 md:grid-cols-2 gap-2",
            ),
            class_name="bg-gray-50 p-4 rounded-xl border border-gray-100 mt-4",
        ),
        class_name="flex flex-col",
    )


def tab_organizacional() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h4(
                "Niveles Administrativos",
                class_name="text-sm font-semibold text-gray-900 mb-3",
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
                class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            rx.el.h4(
                "Clasificación y Atributos",
                class_name="text-sm font-semibold text-gray-900 mb-3",
            ),
            rx.el.div(
                form_select("Cargo", "cargo", EmpleadosState.cat_cargos),
                form_select("Tipo de Empleado", "tipo", EmpleadosState.cat_tipos),
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
                class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
            ),
            class_name="",
        ),
        class_name="flex flex-col",
    )


def tab_permisos() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("shield-check", class_name="w-8 h-8 text-blue-600 mb-3"),
            rx.el.h3(
                "Acceso al Portal de Empleados",
                class_name="text-lg font-medium text-gray-900",
            ),
            rx.el.p(
                "Configure si este empleado puede iniciar sesión en la plataforma web para revisar sus roles de pago y asistencia.",
                class_name="text-sm text-gray-500 mt-1 mb-6 max-w-lg",
            ),
            rx.el.div(
                rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        checked=EmpleadosState.selected_employee["accesoweb"],
                        on_change=lambda v: EmpleadosState.toggle_bool_field(
                            "accesoweb", v
                        ),
                        class_name="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
                    ),
                    rx.el.span(
                        "Habilitar acceso a interfaz web",
                        class_name="ml-3 text-sm font-medium text-gray-900",
                    ),
                    class_name="flex items-center p-4 bg-white border border-gray-200 rounded-xl shadow-sm cursor-pointer hover:border-blue-300 transition-all",
                ),
                class_name="mb-6",
            ),
            rx.cond(
                EmpleadosState.is_pwd_enabled,
                rx.el.div(
                    rx.el.label(
                        "Contraseña de acceso",
                        class_name="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1",
                    ),
                    rx.el.div(
                        rx.icon(
                            "lock",
                            class_name="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400",
                        ),
                        rx.el.input(
                            type="text",
                            default_value=EmpleadosState.selected_employee["pwd"],
                            on_change=lambda v: EmpleadosState.set_field("pwd", v),
                            class_name="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all font-mono",
                        ),
                        class_name="relative max-w-xs",
                    ),
                    rx.el.p(
                        "La contraseña por defecto es '12345678'. Se recomienda cambiarla en el primer inicio de sesión.",
                        class_name="text-xs text-amber-600 mt-2 flex items-center gap-1",
                    ),
                    class_name="animate-in fade-in slide-in-from-top-2 duration-300",
                ),
            ),
            class_name="flex flex-col items-start",
        ),
        class_name="p-6 bg-gray-50/50 rounded-xl border border-gray-100 h-full",
    )


def form_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                EmpleadosState.form_title, class_name="text-xl font-bold text-gray-900"
            ),
            rx.el.div(
                rx.el.button(
                    "Cancelar",
                    on_click=EmpleadosState.cancel_edit,
                    class_name="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors",
                ),
                rx.el.button(
                    rx.icon("save", class_name="w-4 h-4 mr-2"),
                    "Guardar",
                    on_click=EmpleadosState.save_employee,
                    class_name="flex items-center px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm",
                ),
                class_name="flex gap-2",
            ),
            class_name="flex justify-between items-center mb-6 pb-4 border-b",
        ),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger(
                    "Datos Básicos",
                    value="tab1",
                    class_name="px-4 py-2 text-sm font-medium text-gray-600 border-b-2 border-transparent hover:text-gray-800 data-[state=active]:border-blue-600 data-[state=active]:text-blue-600 transition-all",
                ),
                rx.tabs.trigger(
                    "Datos Organizacionales",
                    value="tab2",
                    class_name="px-4 py-2 text-sm font-medium text-gray-600 border-b-2 border-transparent hover:text-gray-800 data-[state=active]:border-blue-600 data-[state=active]:text-blue-600 transition-all",
                ),
                rx.tabs.trigger(
                    "Permisos",
                    value="tab3",
                    class_name="px-4 py-2 text-sm font-medium text-gray-600 border-b-2 border-transparent hover:text-gray-800 data-[state=active]:border-blue-600 data-[state=active]:text-blue-600 transition-all",
                ),
                class_name="flex gap-4 mb-6 border-b border-gray-100",
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
            class_name="flex-1",
        ),
        rx.el.div(
            rx.el.label(
                rx.el.input(
                    type="checkbox",
                    checked=EmpleadosState.selected_employee["activo"],
                    on_change=lambda v: EmpleadosState.toggle_bool_field("activo", v),
                    class_name="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
                ),
                rx.el.span(
                    "Empleado Activo",
                    class_name="ml-2 text-sm font-medium text-gray-900",
                ),
                class_name="flex items-center",
            ),
            class_name="mt-6 pt-4 border-t border-gray-100",
        ),
        class_name="bg-white p-6 rounded-xl shadow-sm border h-full flex flex-col",
        key=EmpleadosState.selected_employee["id"],
    )


def empleados_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Gestión de Empleados",
                class_name="text-2xl font-bold text-gray-900 tracking-tight",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "search",
                            class_name="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400",
                        ),
                        rx.el.input(
                            placeholder="Buscar por nombre o cédula...",
                            on_change=EmpleadosState.set_search_query,
                            class_name="w-full pl-9 pr-4 py-2 rounded-lg border border-gray-200 bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-sm",
                        ),
                        class_name="relative mb-3",
                    ),
                    rx.el.div(
                        rx.el.label(
                            rx.el.input(
                                type="checkbox",
                                checked=EmpleadosState.show_inactive,
                                on_change=EmpleadosState.set_show_inactive,
                                class_name="w-3.5 h-3.5 rounded border-gray-300 text-blue-600 focus:ring-blue-500",
                            ),
                            rx.el.span(
                                "Mostrar inactivos",
                                class_name="ml-2 text-xs font-medium text-gray-600",
                            ),
                            class_name="flex items-center cursor-pointer select-none",
                        ),
                        rx.el.button(
                            rx.icon("plus", class_name="w-3.5 h-3.5 mr-1.5"),
                            "Nuevo",
                            on_click=EmpleadosState.new_employee,
                            class_name="flex items-center px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded-md hover:bg-blue-700 transition-all",
                        ),
                        class_name="flex justify-between items-center mb-4",
                    ),
                    rx.el.div(
                        rx.foreach(
                            EmpleadosState.filtered_employees, employee_list_item
                        ),
                        class_name="space-y-2 overflow-y-auto pr-1 custom-scrollbar flex-1",
                    ),
                    class_name="flex flex-col h-full",
                ),
                class_name="w-full md:w-[320px] bg-white p-4 rounded-xl border border-gray-200 h-[calc(100vh-10rem)] shadow-sm shrink-0",
            ),
            rx.el.div(
                rx.cond(
                    EmpleadosState.is_editing,
                    form_section(),
                    rx.el.div(
                        rx.icon(
                            "user-round-search",
                            class_name="w-16 h-16 text-gray-200 mb-4",
                        ),
                        rx.el.h3(
                            "Seleccione un empleado",
                            class_name="text-lg font-medium text-gray-900 mb-1",
                        ),
                        rx.el.p(
                            "Seleccione un registro de la lista o cree uno nuevo para comenzar.",
                            class_name="text-gray-500 text-center max-w-xs",
                        ),
                        class_name="h-full flex flex-col items-center justify-center bg-gray-50/50 rounded-xl border-2 border-dashed border-gray-200",
                    ),
                ),
                class_name="flex-1 h-[calc(100vh-10rem)] min-w-0",
            ),
            class_name="flex flex-col md:flex-row gap-6",
        ),
        class_name="animate-fade-in-up h-full",
        on_mount=EmpleadosState.on_load,
    )