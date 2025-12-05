import reflex as rx
from app.states.tipo_justificaciones_state import (
    TipoJustificacionesState,
    Justificacion,
)


def form_checkbox(label: str, name: str, checked: bool) -> rx.Component:
    return rx.el.label(
        rx.el.input(
            name=name,
            type="checkbox",
            default_checked=checked,
            class_name="h-4 w-4 rounded border-input text-primary focus:ring-ring",
        ),
        rx.el.span(label, class_name="ml-2 text-sm text-foreground"),
        class_name="flex items-center",
    )


def justificacion_modal() -> rx.Component:
    return rx.el.div(
        rx.cond(
            TipoJustificacionesState.show_modal,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            rx.cond(
                                TipoJustificacionesState.is_editing,
                                "Editar Justificación",
                                "Añadir Justificación",
                            ),
                            class_name="text-lg text-card-foreground",
                        ),
                        rx.el.button(
                            rx.icon("x", class_name="h-5 w-5 text-muted-foreground"),
                            on_click=TipoJustificacionesState.close_modal,
                            class_name="p-1 rounded-full ios-hover",
                        ),
                        class_name="flex justify-between items-center pb-4 border-b",
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.el.label(
                                        "Código Alterno",
                                        class_name="text-sm text-muted-foreground block mb-1",
                                    ),
                                    rx.el.input(
                                        name="cod_alterno",
                                        default_value=TipoJustificacionesState.modal_justificacion[
                                            "cod_alterno"
                                        ],
                                        class_name="w-full px-3 py-2 rounded-lg border-input bg-background shadow-sm focus:ring-2 focus:ring-ring transition-smooth",
                                    ),
                                ),
                                class_name="grid grid-cols-1 gap-4 mb-4",
                            ),
                            rx.el.label(
                                "Descripción",
                                class_name="text-sm text-muted-foreground block mb-1",
                            ),
                            rx.el.textarea(
                                name="descripcion",
                                default_value=TipoJustificacionesState.modal_justificacion[
                                    "descripcion"
                                ],
                                class_name="w-full px-3 py-2 rounded-lg border-input bg-background shadow-sm focus:ring-2 focus:ring-ring transition-smooth mb-4",
                                rows="2",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.label(
                                        "Días máximo",
                                        class_name="text-sm text-muted-foreground block mb-1",
                                    ),
                                    rx.el.input(
                                        name="dias_maximo",
                                        type="number",
                                        default_value=TipoJustificacionesState.modal_justificacion[
                                            "dias_maximo"
                                        ],
                                        class_name="w-full px-3 py-2 rounded-lg border-input bg-background shadow-sm focus:ring-2 focus:ring-ring transition-smooth",
                                    ),
                                ),
                                rx.el.div(
                                    rx.el.label(
                                        "Horas máximo",
                                        class_name="text-sm text-muted-foreground block mb-1",
                                    ),
                                    rx.el.input(
                                        name="horas_maximo",
                                        type="number",
                                        step="0.1",
                                        default_value=TipoJustificacionesState.modal_justificacion[
                                            "horas_maximo"
                                        ],
                                        class_name="w-full px-3 py-2 rounded-lg border-input bg-background shadow-sm focus:ring-2 focus:ring-ring transition-smooth",
                                    ),
                                ),
                                rx.el.div(
                                    rx.el.label(
                                        "Días ingreso",
                                        class_name="text-sm text-muted-foreground block mb-1",
                                    ),
                                    rx.el.input(
                                        name="dias_ingreso",
                                        type="number",
                                        default_value=TipoJustificacionesState.modal_justificacion[
                                            "dias_ingreso"
                                        ],
                                        class_name="w-full px-3 py-2 rounded-lg border-input bg-background shadow-sm focus:ring-2 focus:ring-ring transition-smooth",
                                    ),
                                ),
                                class_name="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4",
                            ),
                            rx.el.div(
                                form_checkbox(
                                    "Faltas",
                                    "completafalta",
                                    TipoJustificacionesState.modal_justificacion[
                                        "completafalta"
                                    ],
                                ),
                                form_checkbox(
                                    "Atraso",
                                    "completaatraso",
                                    TipoJustificacionesState.modal_justificacion[
                                        "completaatraso"
                                    ],
                                ),
                                form_checkbox(
                                    "Justificación",
                                    "justificacion",
                                    TipoJustificacionesState.modal_justificacion[
                                        "justificacion"
                                    ],
                                ),
                                form_checkbox(
                                    "Permiso",
                                    "permiso",
                                    TipoJustificacionesState.modal_justificacion[
                                        "permiso"
                                    ],
                                ),
                                form_checkbox(
                                    "Días hábiles",
                                    "dias_habiles",
                                    TipoJustificacionesState.modal_justificacion[
                                        "dias_habiles"
                                    ],
                                ),
                                form_checkbox(
                                    "Documento Obligatorio",
                                    "documentoobligatorio",
                                    TipoJustificacionesState.modal_justificacion[
                                        "documentoobligatorio"
                                    ],
                                ),
                                form_checkbox(
                                    "Cargo Vacaciones",
                                    "cargovacaciones",
                                    TipoJustificacionesState.modal_justificacion[
                                        "cargovacaciones"
                                    ],
                                ),
                                form_checkbox(
                                    "Acumula Vacaciones",
                                    "acumula_vacaciones",
                                    TipoJustificacionesState.modal_justificacion[
                                        "acumula_vacaciones"
                                    ],
                                ),
                                class_name="grid grid-cols-2 gap-3 mb-4 p-3 bg-muted/30 rounded-lg border",
                            ),
                            form_checkbox(
                                "Activo",
                                "estado",
                                TipoJustificacionesState.modal_justificacion["estado"],
                            ),
                            class_name="py-4 max-h-[70vh] overflow-y-auto pr-2 custom-scrollbar",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Cancelar",
                                on_click=TipoJustificacionesState.close_modal,
                                class_name="px-4 py-2 bg-button-inactive text-button-inactive-foreground rounded-lg border border-button-inactive-border transition-smooth ios-hover",
                            ),
                            rx.el.button(
                                "Guardar",
                                type="submit",
                                class_name="px-4 py-2 bg-primary text-primary-foreground rounded-lg ml-3 transition-smooth ios-hover",
                            ),
                            class_name="flex justify-end pt-4 border-t",
                        ),
                        on_submit=TipoJustificacionesState.handle_submit,
                        reset_on_submit=True,
                    ),
                    class_name="bg-card rounded-xl shadow-xl p-6 w-full max-w-2xl",
                ),
                class_name="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/30 ios-blur",
            ),
        )
    )


def tipo_justificaciones_page() -> rx.Component:
    return rx.el.div(
        justificacion_modal(),
        rx.el.div(
            rx.el.h2("Tipos de Justificación", class_name="text-2xl text-foreground"),
            rx.el.div(
                rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        checked=TipoJustificacionesState.show_inactive,
                        on_change=TipoJustificacionesState.set_show_inactive,
                        class_name="h-4 w-4 rounded border-input text-primary focus:ring-ring",
                    ),
                    rx.el.span(
                        "Mostrar inactivos",
                        class_name="ml-2 text-sm font-medium text-foreground",
                    ),
                    class_name="flex items-center cursor-pointer select-none",
                ),
                class_name="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2",
            ),
            rx.el.button(
                rx.icon("circle_plus", class_name="h-5 w-5 mr-2"),
                "Añadir Tipo",
                on_click=TipoJustificacionesState.open_add_modal,
                class_name="flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-lg shadow-md ios-hover transition-smooth",
            ),
            class_name="flex justify-between items-center mb-6 relative",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Descripción",
                                class_name="px-6 py-3 text-left text-xs text-muted-foreground uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Estado",
                                class_name="px-6 py-3 text-left text-xs text-muted-foreground uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Acciones",
                                class_name="px-6 py-3 text-right text-xs text-muted-foreground uppercase tracking-wider",
                            ),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            TipoJustificacionesState.filtered_justificaciones,
                            lambda j: rx.el.tr(
                                rx.el.td(
                                    j["descripcion"],
                                    class_name="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground",
                                ),
                                rx.el.td(
                                    rx.el.span(
                                        rx.cond(j["estado"], "Activo", "Inactivo"),
                                        class_name=rx.cond(
                                            j["estado"],
                                            "px-2 inline-flex text-xs leading-5 rounded-full bg-green-100 text-green-800",
                                            "px-2 inline-flex text-xs leading-5 rounded-full bg-red-100 text-red-800",
                                        ),
                                    ),
                                    class_name="px-6 py-4 whitespace-nowrap text-sm",
                                ),
                                rx.el.td(
                                    rx.el.button(
                                        rx.icon(
                                            "copy", class_name="h-5 w-5 text-primary"
                                        ),
                                        on_click=lambda: TipoJustificacionesState.open_edit_modal(
                                            j
                                        ),
                                        class_name="p-2 hover:bg-accent rounded-full transition-smooth",
                                    ),
                                    rx.el.button(
                                        rx.icon(
                                            "trash-2",
                                            class_name="h-5 w-5 text-destructive",
                                        ),
                                        on_click=lambda: TipoJustificacionesState.delete_justificacion(
                                            j["id"]
                                        ),
                                        class_name="p-2 hover:bg-accent rounded-full transition-smooth",
                                    ),
                                    class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium",
                                ),
                                class_name="bg-card divide-y divide-border",
                            ),
                        ),
                        class_name="bg-card divide-y divide-border",
                    ),
                    class_name="min-w-full divide-y divide-border",
                ),
                class_name="overflow-hidden border shadow-sm sm:rounded-lg bg-card",
            ),
            class_name="align-middle inline-block min-w-full",
        ),
        class_name="animate-fade-in-up",
    )