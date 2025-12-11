import reflex as rx
from app.states.parametros_generales_state import ParametrosGeneralesState


def level_input(
    label: str, value: str, on_change: rx.event.EventType, disabled: bool = False
) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-gray-700 mb-1"),
        rx.el.input(
            on_change=on_change,
            disabled=disabled,
            class_name=rx.cond(
                disabled,
                "w-full px-4 py-2 rounded-lg border border-gray-200 bg-gray-100 text-gray-500 cursor-not-allowed",
                "w-full px-4 py-2 rounded-lg border border-gray-300 bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all",
            ),
            default_value=value,
        ),
        class_name="w-full",
    )


def parametros_generales_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2("Parámetros Generales", class_name="text-xl text-gray-900"),
            class_name="mb-6",
        ),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger(
                    "Niveles Administrativos",
                    value="tab1",
                    class_name="px-3 py-1.5 text-xs font-medium text-gray-600 border-b-2 border-transparent hover:text-gray-800 hover:border-gray-300 data-[state=active]:border-blue-500 data-[state=active]:text-blue-600 transition-colors cursor-pointer",
                ),
                rx.tabs.trigger(
                    "Parámetros Adicionales",
                    value="tab2",
                    class_name="px-3 py-1.5 text-xs font-medium text-gray-600 border-b-2 border-transparent hover:text-gray-800 hover:border-gray-300 data-[state=active]:border-blue-500 data-[state=active]:text-blue-600 transition-colors cursor-pointer",
                ),
                class_name="flex border-b border-gray-200 mb-4",
            ),
            rx.tabs.content(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Niveles Administrativos habilitados",
                                class_name="block text-sm font-bold text-gray-700 mb-2",
                            ),
                            rx.el.div(
                                rx.el.input(
                                    type="number",
                                    on_change=ParametrosGeneralesState.set_niveles_habilitados,
                                    min="1",
                                    max="5",
                                    class_name="w-24 px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-center",
                                    default_value=ParametrosGeneralesState.niveles_habilitados,
                                ),
                                class_name="flex items-center",
                            ),
                            class_name="mb-8 p-4 bg-blue-50/50 rounded-xl border border-blue-100 flex flex-col items-center justify-center",
                        ),
                        rx.el.div(
                            level_input(
                                "Nivel 1",
                                ParametrosGeneralesState.nivel_1,
                                ParametrosGeneralesState.set_nivel_1,
                                disabled=ParametrosGeneralesState.niveles_habilitados
                                < 1,
                            ),
                            level_input(
                                "Nivel 2",
                                ParametrosGeneralesState.nivel_2,
                                ParametrosGeneralesState.set_nivel_2,
                                disabled=ParametrosGeneralesState.niveles_habilitados
                                < 2,
                            ),
                            level_input(
                                "Nivel 3",
                                ParametrosGeneralesState.nivel_3,
                                ParametrosGeneralesState.set_nivel_3,
                                disabled=ParametrosGeneralesState.niveles_habilitados
                                < 3,
                            ),
                            level_input(
                                "Nivel 4",
                                ParametrosGeneralesState.nivel_4,
                                ParametrosGeneralesState.set_nivel_4,
                                disabled=ParametrosGeneralesState.niveles_habilitados
                                < 4,
                            ),
                            level_input(
                                "Nivel 5",
                                ParametrosGeneralesState.nivel_5,
                                ParametrosGeneralesState.set_nivel_5,
                                disabled=ParametrosGeneralesState.niveles_habilitados
                                < 5,
                            ),
                            class_name="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.label(
                                    rx.el.input(
                                        type="checkbox",
                                        checked=ParametrosGeneralesState.asociar_calendario,
                                        on_change=ParametrosGeneralesState.set_asociar_calendario,
                                        class_name="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
                                    ),
                                    rx.el.span(
                                        "Asociar Calendario de feriados con niveles Administrativos",
                                        class_name="ml-3 text-sm font-medium text-gray-700",
                                    ),
                                    class_name="flex items-center h-full",
                                ),
                                class_name="flex items-center",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Nivel de asociación",
                                    class_name="block text-sm font-medium text-gray-700 mb-1",
                                ),
                                rx.el.select(
                                    rx.foreach(
                                        ParametrosGeneralesState.association_levels,
                                        lambda x: rx.el.option(x, value=x),
                                    ),
                                    value=ParametrosGeneralesState.nivel_asociacion,
                                    on_change=ParametrosGeneralesState.set_nivel_asociacion,
                                    disabled=~ParametrosGeneralesState.asociar_calendario,
                                    class_name=rx.cond(
                                        ParametrosGeneralesState.asociar_calendario,
                                        "w-full px-4 py-2 rounded-lg border border-gray-300 bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all",
                                        "w-full px-4 py-2 rounded-lg border border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed transition-all",
                                    ),
                                ),
                                class_name="w-full max-w-xs",
                            ),
                            class_name="flex flex-col md:flex-row md:items-center gap-6 p-6 bg-gray-50 rounded-xl border border-gray-200",
                        ),
                        class_name="flex flex-col",
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.cond(
                                ParametrosGeneralesState.is_loading,
                                rx.el.div(
                                    class_name="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"
                                ),
                                rx.el.span(
                                    rx.icon("save", class_name="h-5 w-5 mr-2"),
                                    "Guardar Cambios",
                                    class_name="flex items-center",
                                ),
                            ),
                            on_click=ParametrosGeneralesState.save_parameters,
                            disabled=ParametrosGeneralesState.is_loading,
                            class_name="flex items-center justify-center px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl shadow-lg hover:shadow-blue-500/30 transition-all active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed",
                        ),
                        class_name="flex justify-end mt-8 pt-6 border-t border-gray-100",
                    ),
                    class_name="bg-white p-8 rounded-2xl shadow-sm border border-gray-200",
                ),
                value="tab1",
            ),
            rx.tabs.content(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            "Atributos de Empleados",
                            class_name="text-lg font-medium text-gray-900 mb-4 text-center",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.el.label(
                                        rx.el.input(
                                            type="checkbox",
                                            checked=ParametrosGeneralesState.param_35
                                            == "1",
                                            on_change=ParametrosGeneralesState.set_param_35,
                                            class_name="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
                                        ),
                                        rx.el.div(
                                            rx.el.span(
                                                "Agregar a la información de empleados un atributo tabular (numérico)",
                                                class_name="text-sm font-medium text-gray-700",
                                            ),
                                            rx.el.p(
                                                "Permite asignar un valor numérico adicional a la ficha de cada empleado.",
                                                class_name="text-xs text-gray-500 mt-0.5",
                                            ),
                                            class_name="flex flex-col ml-3",
                                        ),
                                        class_name="flex items-start mb-4",
                                    ),
                                    rx.el.div(
                                        rx.el.label(
                                            "Descripción del atributo",
                                            class_name="block text-sm font-medium text-gray-700 mb-1",
                                        ),
                                        rx.el.input(
                                            on_change=ParametrosGeneralesState.set_param_36,
                                            disabled=ParametrosGeneralesState.param_35
                                            != "1",
                                            placeholder="Ej: Bono Productividad",
                                            class_name=rx.cond(
                                                ParametrosGeneralesState.param_35
                                                != "1",
                                                "w-full px-4 py-2 rounded-lg border border-gray-200 bg-gray-100 text-gray-500 cursor-not-allowed",
                                                "w-full px-4 py-2 rounded-lg border border-gray-300 bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all",
                                            ),
                                            default_value=ParametrosGeneralesState.param_36,
                                        ),
                                        class_name="pl-7",
                                    ),
                                    class_name="p-4 bg-gray-50 rounded-xl border border-gray-200",
                                )
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.label(
                                        rx.el.input(
                                            type="checkbox",
                                            checked=ParametrosGeneralesState.param_39
                                            == "1",
                                            on_change=ParametrosGeneralesState.set_param_39,
                                            class_name="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
                                        ),
                                        rx.el.div(
                                            rx.el.span(
                                                "Agregar a la información de los empleados un atributo de texto",
                                                class_name="text-sm font-medium text-gray-700",
                                            ),
                                            rx.el.p(
                                                "Permite asignar un campo de texto adicional a la ficha de cada empleado.",
                                                class_name="text-xs text-gray-500 mt-0.5",
                                            ),
                                            class_name="flex flex-col ml-3",
                                        ),
                                        class_name="flex items-start mb-4",
                                    ),
                                    rx.el.div(
                                        rx.el.label(
                                            "Descripción del atributo",
                                            class_name="block text-sm font-medium text-gray-700 mb-1",
                                        ),
                                        rx.el.input(
                                            on_change=ParametrosGeneralesState.set_param_40,
                                            disabled=ParametrosGeneralesState.param_39
                                            != "1",
                                            placeholder="Ej: Código de Proyecto",
                                            class_name=rx.cond(
                                                ParametrosGeneralesState.param_39
                                                != "1",
                                                "w-full px-4 py-2 rounded-lg border border-gray-200 bg-gray-100 text-gray-500 cursor-not-allowed",
                                                "w-full px-4 py-2 rounded-lg border border-gray-300 bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all",
                                            ),
                                            default_value=ParametrosGeneralesState.param_40,
                                        ),
                                        class_name="pl-7",
                                    ),
                                    class_name="p-4 bg-gray-50 rounded-xl border border-gray-200",
                                )
                            ),
                            class_name="space-y-6",
                        ),
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.cond(
                                ParametrosGeneralesState.is_loading,
                                rx.el.div(
                                    class_name="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"
                                ),
                                rx.el.span(
                                    rx.icon("save", class_name="h-5 w-5 mr-2"),
                                    "Guardar Cambios",
                                    class_name="flex items-center",
                                ),
                            ),
                            on_click=ParametrosGeneralesState.save_parameters,
                            disabled=ParametrosGeneralesState.is_loading,
                            class_name="flex items-center justify-center px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl shadow-lg hover:shadow-blue-500/30 transition-all active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed",
                        ),
                        class_name="flex justify-end mt-8 pt-6 border-t border-gray-100",
                    ),
                    class_name="bg-white p-8 rounded-2xl shadow-sm border border-gray-200",
                ),
                value="tab2",
            ),
            default_value="tab1",
            class_name="w-full",
        ),
        class_name="animate-fade-in-up max-w-5xl mx-auto",
        id="parametros-generales-root",
        on_mount=ParametrosGeneralesState.on_load,
    )