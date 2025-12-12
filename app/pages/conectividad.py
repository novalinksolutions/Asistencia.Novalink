import reflex as rx
from app.states.conectividad_state import ConectividadState


def status_badge(active: bool, text_true: str, text_false: str) -> rx.Component:
    return rx.el.span(
        rx.cond(active, text_true, text_false),
        class_name=rx.cond(
            active,
            "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800",
            "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800",
        ),
    )


def dispositivo_row(dispositivo: dict) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            dispositivo["codigo"],
            class_name="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900",
        ),
        rx.el.td(
            dispositivo["descripcion"],
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            status_badge(dispositivo["activo"], "Activo", "Inactivo"),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            status_badge(dispositivo["en_linea"], "Conectado", "Desconectado"),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.button(
                rx.icon("pencil", class_name="h-4 w-4"),
                on_click=lambda: ConectividadState.open_dialog(dispositivo),
                class_name="text-blue-600 hover:text-blue-900 p-2 hover:bg-blue-50 rounded-full transition-colors",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium",
        ),
        class_name="hover:bg-gray-50 transition-colors",
    )


def dispositivo_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    ConectividadState.current_dispositivo["id"] == 0,
                    "Nuevo Dispositivo",
                    "Editar Dispositivo",
                ),
                class_name="text-lg font-bold text-gray-900 mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Código",
                        class_name="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1",
                    ),
                    rx.el.input(
                        on_change=lambda v: ConectividadState.update_current_field(
                            "codigo", v
                        ),
                        class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white",
                        default_value=ConectividadState.current_dispositivo["codigo"],
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label(
                        "Descripción",
                        class_name="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1",
                    ),
                    rx.el.input(
                        on_change=lambda v: ConectividadState.update_current_field(
                            "descripcion", v
                        ),
                        class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white",
                        default_value=ConectividadState.current_dispositivo[
                            "descripcion"
                        ],
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            checked=ConectividadState.current_dispositivo["activo"],
                            on_change=lambda v: ConectividadState.update_current_field(
                                "activo", v
                            ),
                            class_name="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
                        ),
                        rx.el.span("Activo", class_name="ml-2 text-sm text-gray-700"),
                        class_name="flex items-center p-2 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer",
                    ),
                    class_name="mb-4",
                ),
                rx.cond(
                    ConectividadState.error_message != "",
                    rx.el.p(
                        ConectividadState.error_message,
                        class_name="text-sm text-red-600 mb-4",
                    ),
                    None,
                ),
                class_name="flex flex-col",
            ),
            rx.el.div(
                rx.el.button(
                    "Cancelar",
                    on_click=ConectividadState.close_dialog,
                    class_name="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors",
                ),
                rx.el.button(
                    "Guardar",
                    on_click=ConectividadState.save_dispositivo,
                    class_name="flex items-center px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm",
                ),
                class_name="flex justify-end gap-3 mt-6",
            ),
            class_name="bg-white rounded-xl p-6 w-full max-w-md shadow-xl",
        ),
        open=ConectividadState.show_dialog,
        on_open_change=lambda v: ConectividadState.close_dialog(),
    )


def conectividad_page() -> rx.Component:
    return rx.el.div(
        dispositivo_dialog(),
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Conectividad de Dispositivos",
                    class_name="text-2xl text-foreground",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4 mr-2"),
                    "Nuevo Dispositivo",
                    on_click=lambda: ConectividadState.open_dialog(None),
                    class_name="flex items-center px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm",
                ),
                class_name="flex justify-between items-center mb-6",
            ),
            rx.el.div(
                rx.el.input(
                    placeholder="Buscar por código o descripción...",
                    on_change=ConectividadState.set_search_query,
                    class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white text-sm",
                    default_value=ConectividadState.search_query,
                ),
                class_name="mb-6 max-w-lg",
            ),
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Código",
                                class_name="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Descripción",
                                class_name="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Estado",
                                class_name="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Conectividad",
                                class_name="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th("", class_name="px-6 py-3 bg-gray-50"),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            ConectividadState.filtered_dispositivos, dispositivo_row
                        ),
                        class_name="bg-white divide-y divide-gray-200",
                    ),
                    class_name="min-w-full divide-y divide-gray-200",
                ),
                class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg",
            ),
            class_name="animate-fade-in-up",
        ),
        class_name="w-full",
    )