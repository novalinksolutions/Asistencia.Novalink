import reflex as rx
from app.states.catalogo_nivel1_state import CatalogoNivel1State
from app.states.parametros_generales_state import ParametrosGeneralesState


def list_item(item: dict) -> rx.Component:
    is_selected = CatalogoNivel1State.selected_item["codigo"] == item["codigo"]
    return rx.el.div(
        rx.el.div(
            rx.el.p(item["descripcion"], class_name="font-medium text-sm"),
            rx.el.p(
                f"Código: {item['codigo']}", class_name="text-xs text-muted-foreground"
            ),
        ),
        on_click=lambda: CatalogoNivel1State.select_item(item),
        class_name=rx.cond(
            is_selected,
            "p-3 rounded-lg bg-blue-50 border border-blue-200 cursor-pointer transition-all",
            rx.cond(
                item["activo"],
                "p-3 rounded-lg hover:bg-gray-50 cursor-pointer border border-transparent transition-all",
                "p-3 rounded-lg bg-gray-50 opacity-60 cursor-pointer border border-transparent transition-all grayscale",
            ),
        ),
    )


def form_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                rx.cond(
                    CatalogoNivel1State.selected_item["codigo"] == 0,
                    "Nuevo Registro",
                    "Editar Registro",
                ),
                class_name="text-lg font-bold text-gray-900",
            ),
            rx.el.div(
                rx.el.button(
                    "Cancelar",
                    on_click=CatalogoNivel1State.cancel_edit,
                    class_name="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors",
                ),
                rx.el.button(
                    rx.icon("save", class_name="w-4 h-4 mr-2"),
                    "Guardar",
                    on_click=CatalogoNivel1State.save_item,
                    class_name="flex items-center px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm",
                ),
                class_name="flex gap-2",
            ),
            class_name="flex justify-between items-center mb-6 pb-4 border-b",
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
                    default_value=CatalogoNivel1State.selected_item["codigo"],
                    key=CatalogoNivel1State.selected_item["codigo"],
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.label(
                    "Descripción",
                    class_name="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1",
                ),
                rx.el.input(
                    on_change=CatalogoNivel1State.set_selected_item_description,
                    placeholder="Ingrese la descripción...",
                    class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white",
                    default_value=CatalogoNivel1State.selected_item["descripcion"],
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        checked=CatalogoNivel1State.selected_item["activo"],
                        on_change=CatalogoNivel1State.set_selected_item_active,
                        class_name="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
                    ),
                    rx.el.span(
                        "Registro Activo", class_name="ml-2 text-sm text-gray-700"
                    ),
                    class_name="flex items-center p-2 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer",
                ),
                class_name="mb-6",
            ),
            rx.cond(
                CatalogoNivel1State.selected_item["codigo"] != 0,
                rx.el.div(
                    rx.el.div(
                        rx.el.span(
                            "Fecha Creación:", class_name="text-xs text-gray-500"
                        ),
                        rx.el.span(
                            CatalogoNivel1State.selected_item["fecha_creacion"],
                            class_name="text-xs font-medium ml-1",
                        ),
                        class_name="flex items-center",
                    ),
                    rx.el.div(
                        rx.el.span(
                            "Última Modificación:", class_name="text-xs text-gray-500"
                        ),
                        rx.el.span(
                            CatalogoNivel1State.selected_item["fecha_modificacion"],
                            class_name="text-xs font-medium ml-1",
                        ),
                        class_name="flex items-center mt-1",
                    ),
                    class_name="p-3 bg-gray-50 rounded-lg border border-gray-100",
                ),
                None,
            ),
            class_name="max-w-md",
        ),
        class_name="bg-white p-6 rounded-xl shadow-sm border h-full",
    )


def catalogo_nivel1_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                ParametrosGeneralesState.nivel_1,
                class_name="text-2xl font-bold text-gray-900",
            ),
            rx.el.div(
                rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        checked=CatalogoNivel1State.show_inactive,
                        on_change=CatalogoNivel1State.set_show_inactive,
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
                    on_click=CatalogoNivel1State.new_item,
                    class_name="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-sm transition-all",
                ),
                class_name="flex items-center",
            ),
            class_name="flex justify-between items-center mb-6",
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
                        on_change=CatalogoNivel1State.set_search_query,
                        class_name="w-full pl-9 pr-4 py-2 rounded-lg border border-gray-200 bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-sm mb-4",
                    ),
                    class_name="relative",
                ),
                rx.el.div(
                    rx.foreach(CatalogoNivel1State.filtered_items, list_item),
                    class_name="space-y-2 overflow-y-auto pr-2 custom-scrollbar flex-1",
                ),
                class_name="w-[30%] min-w-[250px] flex flex-col h-[calc(100vh-12rem)]",
            ),
            rx.el.div(
                rx.cond(
                    CatalogoNivel1State.is_editing,
                    form_section(),
                    rx.el.div(
                        rx.icon(
                            "mouse-pointer-click",
                            class_name="w-12 h-12 text-gray-300 mb-4",
                        ),
                        rx.el.p(
                            "Seleccione un registro para editar o cree uno nuevo",
                            class_name="text-gray-500",
                        ),
                        class_name="h-full flex flex-col items-center justify-center bg-gray-50 rounded-xl border border-dashed border-gray-200",
                    ),
                ),
                class_name="flex-1 h-[calc(100vh-12rem)]",
            ),
            class_name="flex gap-6",
        ),
        class_name="animate-fade-in-up h-full",
    )