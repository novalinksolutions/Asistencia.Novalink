import reflex as rx
from app.states.entidades_state import EntidadesState
from app.states.parametros_generales_state import ParametrosGeneralesState


def entidad_list_item(item: dict) -> rx.Component:
    is_selected = EntidadesState.selected_item["codigo"] == item["codigo"]
    return rx.el.div(
        rx.el.div(
            rx.el.p(item["descripcion"], class_name="font-medium text-sm"),
            rx.el.div(
                rx.el.p(
                    f"Código: {item['codigo']}",
                    class_name="text-xs text-muted-foreground",
                ),
                class_name="flex items-center gap-2",
            ),
        ),
        on_click=lambda: EntidadesState.select_item(item),
        class_name=rx.cond(
            is_selected,
            "p-3 rounded-lg bg-blue-50 border border-blue-200 cursor-pointer transition-all",
            rx.cond(
                item["activo"],
                "p-3 rounded-lg hover:bg-gray-50 cursor-pointer border border-transparent transition-all",
                "p-3 rounded-lg bg-gray-100 opacity-60 cursor-pointer border border-gray-200 transition-all",
            ),
        ),
    )


def form_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    rx.cond(
                        EntidadesState.selected_item["codigo"] == 0,
                        "Nueva Entidad",
                        "Editar Entidad",
                    ),
                    class_name="text-xl font-bold text-gray-900",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancelar",
                        on_click=EntidadesState.cancel_edit,
                        class_name="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors",
                    ),
                    rx.el.button(
                        rx.icon("save", class_name="w-4 h-4 mr-2"),
                        "Guardar",
                        on_click=EntidadesState.save_item,
                        class_name="flex items-center px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm",
                    ),
                    class_name="flex gap-2",
                ),
                class_name="flex justify-between items-center pb-6 border-b",
            ),
            rx.el.div(
                rx.el.h4(
                    "Información General",
                    class_name="text-xs font-medium text-gray-500 uppercase tracking-wider mb-4 mt-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Código",
                            class_name="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1",
                        ),
                        rx.el.input(
                            read_only=True,
                            class_name="w-full px-3 py-2 bg-gray-100 border border-gray-200 rounded-lg text-gray-500 cursor-not-allowed",
                            default_value=EntidadesState.selected_item["codigo"],
                            key=EntidadesState.selected_item["codigo"],
                        ),
                    ),
                    rx.cond(
                        (EntidadesState.selected_nivel == "2")
                        | (EntidadesState.selected_nivel == "cargos")
                        | (EntidadesState.selected_nivel == "grupos")
                        | (EntidadesState.selected_nivel == "atributo"),
                        rx.el.div(
                            rx.el.label(
                                ParametrosGeneralesState.nivel_1,
                                class_name="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1",
                            ),
                            rx.el.select(
                                rx.el.option("Seleccione...", value=""),
                                rx.foreach(
                                    EntidadesState.parent_items_nivel1,
                                    lambda x: rx.el.option(
                                        x["descripcion"], value=x["codigo"]
                                    ),
                                ),
                                value=EntidadesState.selected_parent_nivel1,
                                on_change=EntidadesState.set_selected_parent_nivel1,
                                class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white",
                            ),
                            class_name="col-span-2",
                        ),
                    ),
                    rx.cond(
                        EntidadesState.selected_nivel == "3",
                        rx.el.div(
                            rx.el.label(
                                ParametrosGeneralesState.nivel_2,
                                class_name="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1",
                            ),
                            rx.el.select(
                                rx.el.option("Seleccione...", value=""),
                                rx.foreach(
                                    EntidadesState.parent_items_nivel2,
                                    lambda x: rx.el.option(
                                        x["descripcion"], value=x["codigo"]
                                    ),
                                ),
                                value=EntidadesState.selected_parent_nivel2,
                                on_change=EntidadesState.set_selected_parent_nivel2,
                                class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white",
                            ),
                            class_name="col-span-2",
                        ),
                    ),
                    rx.cond(
                        EntidadesState.selected_nivel == "4",
                        rx.el.div(
                            rx.el.label(
                                ParametrosGeneralesState.nivel_3,
                                class_name="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1",
                            ),
                            rx.el.select(
                                rx.el.option("Seleccione...", value=""),
                                rx.foreach(
                                    EntidadesState.parent_items_nivel3,
                                    lambda x: rx.el.option(
                                        x["descripcion"], value=x["codigo"]
                                    ),
                                ),
                                value=EntidadesState.selected_parent_nivel3,
                                on_change=EntidadesState.set_selected_parent_nivel3,
                                class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white",
                            ),
                            class_name="col-span-2",
                        ),
                    ),
                    rx.cond(
                        EntidadesState.selected_nivel == "5",
                        rx.el.div(
                            rx.el.label(
                                ParametrosGeneralesState.nivel_4,
                                class_name="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1",
                            ),
                            rx.el.select(
                                rx.el.option("Seleccione...", value=""),
                                rx.foreach(
                                    EntidadesState.parent_items_nivel4,
                                    lambda x: rx.el.option(
                                        x["descripcion"], value=x["codigo"]
                                    ),
                                ),
                                value=EntidadesState.selected_parent_nivel4,
                                on_change=EntidadesState.set_selected_parent_nivel4,
                                class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white",
                            ),
                            class_name="col-span-2",
                        ),
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Descripción",
                            class_name="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1",
                        ),
                        rx.el.input(
                            on_change=EntidadesState.set_selected_item_description,
                            placeholder="Ingrese el nombre o descripción...",
                            class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white",
                            default_value=EntidadesState.selected_item["descripcion"],
                        ),
                        class_name="col-span-3",
                    ),
                    rx.el.div(
                        rx.el.label(
                            rx.el.input(
                                type="checkbox",
                                checked=EntidadesState.selected_item["activo"],
                                on_change=EntidadesState.set_selected_item_active,
                                class_name="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
                            ),
                            rx.el.span(
                                "Registro Activo",
                                class_name="ml-2 text-sm text-gray-700",
                            ),
                            class_name="flex items-center p-2 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer",
                        ),
                        class_name="col-span-3",
                    ),
                    class_name="grid grid-cols-3 gap-4 mb-8",
                ),
                rx.cond(
                    EntidadesState.selected_item["codigo"] != 0,
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(
                                "Fecha Creación:", class_name="text-xs text-gray-500"
                            ),
                            rx.el.span(
                                EntidadesState.selected_item["fecha_creacion"],
                                class_name="text-xs font-medium ml-1",
                            ),
                            class_name="flex items-center",
                        ),
                        rx.el.div(
                            rx.el.span(
                                "Creado por:", class_name="text-xs text-gray-500"
                            ),
                            rx.el.span(
                                EntidadesState.selected_item["usuario"],
                                class_name="text-xs font-medium ml-1",
                            ),
                            class_name="flex items-center ml-4",
                        ),
                        class_name="flex items-center p-3 bg-gray-50 rounded-lg border border-gray-100",
                    ),
                    None,
                ),
                class_name="flex-1 overflow-y-auto pr-2 custom-scrollbar",
            ),
            class_name="flex flex-col h-full overflow-hidden",
        ),
        class_name="bg-white p-6 rounded-xl shadow-sm border h-full flex flex-col",
        key=f"{EntidadesState.selected_nivel}_{EntidadesState.selected_item['codigo']}",
    )


def entidades_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Gestión de Entidades",
                class_name="text-2xl font-bold text-gray-900 tracking-tight",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Nivel Administrativo:",
                    class_name="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5",
                ),
                rx.el.select(
                    rx.foreach(
                        EntidadesState.niveles_config,
                        lambda n: rx.el.option(n["label"], value=n["id"].to(str)),
                    ),
                    value=EntidadesState.selected_nivel,
                    on_change=EntidadesState.set_selected_nivel,
                    class_name="w-full md:w-64 px-3 py-2 rounded-lg border border-gray-300 bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-sm shadow-sm",
                ),
                class_name="flex-1 md:flex-none",
            ),
            rx.el.div(
                rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        checked=EntidadesState.show_inactive,
                        on_change=EntidadesState.set_show_inactive,
                        class_name="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500",
                    ),
                    rx.el.span(
                        "Mostrar inactivos",
                        class_name="ml-2 text-sm font-medium text-gray-700",
                    ),
                    class_name="flex items-center cursor-pointer select-none mr-4",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="w-4 h-4 mr-2"),
                    "Nuevo",
                    on_click=EntidadesState.new_item,
                    class_name="flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 shadow-sm hover:shadow-md transition-all active:scale-95",
                ),
                class_name="flex items-center gap-3",
            ),
            class_name="flex flex-col md:flex-row justify-between items-end md:items-center gap-4 mb-6 bg-white p-4 rounded-xl border border-gray-100 shadow-sm",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400",
                    ),
                    rx.el.input(
                        placeholder="Buscar...",
                        on_change=EntidadesState.set_search_query,
                        class_name="w-full pl-9 pr-4 py-2 rounded-lg border border-gray-200 bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-sm mb-4",
                    ),
                    class_name="relative",
                ),
                rx.el.div(
                    rx.foreach(EntidadesState.filtered_items, entidad_list_item),
                    class_name="space-y-2 overflow-y-auto pr-2 custom-scrollbar flex-1",
                ),
                class_name="w-full md:w-[35%] min-w-[300px] flex flex-col h-[calc(100vh-13rem)]",
            ),
            rx.el.div(
                rx.cond(
                    EntidadesState.is_editing,
                    form_section(),
                    rx.el.div(
                        rx.icon(
                            "mouse-pointer-click",
                            class_name="w-12 h-12 text-gray-200 mb-4",
                        ),
                        rx.el.p(
                            "Seleccione un registro para editar o cree uno nuevo",
                            class_name="text-gray-400 font-medium",
                        ),
                        class_name="h-full flex flex-col items-center justify-center bg-gray-50/50 rounded-xl border border-dashed border-gray-200",
                    ),
                ),
                class_name="flex-1 h-[calc(100vh-13rem)]",
            ),
            class_name="flex flex-col md:flex-row gap-6",
        ),
        class_name="animate-fade-in-up h-full",
        on_mount=EntidadesState.on_load,
    )