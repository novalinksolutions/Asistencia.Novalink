import reflex as rx
from app.states.transacciones_state import TransaccionesState


def transaccion_row(transaccion: dict) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            transaccion["dispositivo"],
            class_name="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900",
        ),
        rx.el.td(
            transaccion["fechahora"],
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(transaccion["mensaje"], class_name="px-6 py-4 text-sm text-gray-500"),
        class_name="hover:bg-gray-50 transition-colors",
    )


def transacciones_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h2("Transacciones", class_name="text-2xl text-foreground"),
                rx.el.button(
                    rx.icon("refresh-ccw", class_name="h-4 w-4 mr-2"),
                    "Actualizar",
                    on_click=TransaccionesState.load_transacciones,
                    class_name="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500",
                ),
                class_name="flex justify-between items-center mb-6",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Filtrar por Dispositivo:",
                        class_name="block text-sm font-medium text-gray-700 mb-1",
                    ),
                    rx.el.select(
                        rx.el.option("Todos los dispositivos", value=""),
                        rx.foreach(
                            TransaccionesState.dispositivos_filter,
                            lambda d: rx.el.option(d["descripcion"], value=d["id"]),
                        ),
                        value=TransaccionesState.selected_dispositivo_id,
                        on_change=TransaccionesState.set_device_filter,
                        class_name="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md",
                    ),
                    class_name="w-full max-w-xs",
                ),
                rx.el.div(
                    rx.el.span(
                        "Mostrando transacciones del día actual",
                        class_name="text-sm text-gray-500 italic",
                    ),
                    class_name="flex items-end pb-2",
                ),
                class_name="flex justify-between items-end mb-6 bg-gray-50 p-4 rounded-lg border border-gray-200",
            ),
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Dispositivo",
                                class_name="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Fecha y Hora",
                                class_name="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Mensaje",
                                class_name="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                        )
                    ),
                    rx.el.tbody(
                        rx.cond(
                            TransaccionesState.transacciones.length() > 0,
                            rx.foreach(
                                TransaccionesState.transacciones, transaccion_row
                            ),
                            rx.el.tr(
                                rx.el.td(
                                    "No se encontraron transacciones para el día de hoy.",
                                    col_span=3,
                                    class_name="px-6 py-8 text-center text-gray-500",
                                )
                            ),
                        ),
                        class_name="bg-white divide-y divide-gray-200",
                    ),
                    class_name="min-w-full divide-y divide-gray-200",
                ),
                class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg mb-4",
            ),
            rx.cond(
                TransaccionesState.total_pages > 1,
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Página ",
                            rx.el.span(
                                TransaccionesState.current_page,
                                class_name="font-medium",
                            ),
                            " de ",
                            rx.el.span(
                                TransaccionesState.total_pages, class_name="font-medium"
                            ),
                            class_name="text-sm text-gray-700",
                        )
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Anterior",
                            on_click=TransaccionesState.prev_page,
                            disabled=~TransaccionesState.has_prev,
                            class_name="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed",
                        ),
                        rx.el.button(
                            "Siguiente",
                            on_click=TransaccionesState.next_page,
                            disabled=~TransaccionesState.has_next,
                            class_name="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed",
                        ),
                        class_name="flex",
                    ),
                    class_name="flex items-center justify-between bg-white px-4 py-3 border-t border-gray-200 sm:px-6",
                ),
                None,
            ),
            class_name="animate-fade-in-up",
        ),
        class_name="w-full",
    )