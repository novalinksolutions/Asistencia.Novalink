import reflex as rx
from app.states.usuarios_state import UsuariosState


def user_modal() -> rx.Component:
    return rx.el.div(
        rx.cond(
            UsuariosState.show_modal,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            rx.cond(
                                UsuariosState.is_editing,
                                "Editar Usuario",
                                "Añadir Usuario",
                            ),
                            class_name="text-lg text-card-foreground",
                        ),
                        rx.el.button(
                            rx.icon("x", class_name="h-5 w-5 text-muted-foreground"),
                            on_click=UsuariosState.close_modal,
                            class_name="p-1 rounded-full ios-hover",
                        ),
                        class_name="flex justify-between items-center pb-4 border-b",
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.label(
                                "Usuario", class_name="text-sm text-muted-foreground"
                            ),
                            rx.el.input(
                                name="name",
                                max_length=20,
                                default_value=UsuariosState.modal_user["name"],
                                placeholder="Ej: jdoe",
                                class_name="mt-1 w-full px-5 py-2 rounded-lg border-input bg-background shadow-sm focus:ring-2 focus:ring-ring transition-smooth",
                            ),
                            rx.el.label(
                                "Descripción",
                                class_name="text-sm mt-4 text-muted-foreground",
                            ),
                            rx.el.input(
                                name="description",
                                max_length=50,
                                default_value=UsuariosState.modal_user["description"],
                                placeholder="Ej: John Doe - Admin",
                                class_name="mt-1 w-full px-5 py-2 rounded-lg border-input bg-background shadow-sm focus:ring-2 focus:ring-ring transition-smooth",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    rx.el.input(
                                        name="active",
                                        type="checkbox",
                                        default_checked=UsuariosState.modal_user[
                                            "active"
                                        ],
                                        class_name="h-4 w-4 rounded border-input text-primary focus:ring-ring",
                                    ),
                                    rx.el.span(
                                        "Activo",
                                        class_name="ml-2 text-sm text-foreground",
                                    ),
                                    class_name="flex items-center",
                                ),
                                class_name="flex flex-col gap-3 mt-4 bg-muted/50 p-3 rounded-lg border",
                            ),
                            class_name="py-4",
                        ),
                        rx.el.div(
                            rx.cond(
                                UsuariosState.is_editing,
                                rx.el.button(
                                    rx.icon("lock-keyhole", class_name="h-4 w-4 mr-2"),
                                    "Restablecer Contraseña",
                                    type="button",
                                    on_click=UsuariosState.reset_user_password,
                                    class_name="flex items-center px-4 py-2 bg-amber-100 text-amber-800 border border-amber-200 rounded-lg hover:bg-amber-200 transition-smooth ios-hover mr-auto",
                                ),
                                None,
                            ),
                            rx.el.button(
                                "Cancelar",
                                on_click=UsuariosState.close_modal,
                                class_name="px-4 py-2 bg-button-inactive text-button-inactive-foreground rounded-lg border border-button-inactive-border transition-smooth ios-hover",
                            ),
                            rx.el.button(
                                "Guardar",
                                type="submit",
                                class_name="px-4 py-2 bg-primary text-primary-foreground rounded-lg ml-3 transition-smooth ios-hover",
                            ),
                            class_name="flex items-center justify-end pt-4 border-t gap-3",
                        ),
                        on_submit=UsuariosState.handle_submit,
                        reset_on_submit=True,
                    ),
                    class_name="bg-card rounded-xl shadow-xl p-6 w-full max-w-lg",
                ),
                class_name="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/30 ios-blur",
            ),
        )
    )


def delete_confirmation_dialog() -> rx.Component:
    return rx.el.div(
        rx.cond(
            UsuariosState.show_delete_confirm,
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Confirmar Eliminación",
                        class_name="text-lg text-card-foreground",
                    ),
                    rx.el.p(
                        f"¿Está seguro de que desea desactivar al usuario '{UsuariosState.user_to_delete['name']}'?",
                        class_name="mt-2 text-sm text-muted-foreground",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancelar",
                            on_click=UsuariosState.cancel_delete,
                            class_name="mt-4 px-4 py-2 bg-button-inactive text-button-inactive-foreground rounded-lg border border-button-inactive-border transition-smooth ios-hover",
                        ),
                        rx.el.button(
                            "Desactivar",
                            on_click=UsuariosState.delete_user,
                            class_name="mt-4 ml-3 px-4 py-2 bg-destructive text-destructive-foreground rounded-lg transition-smooth ios-hover",
                        ),
                        class_name="flex justify-end",
                    ),
                    class_name="bg-card p-6 rounded-xl shadow-lg w-full max-w-sm",
                ),
                class_name="fixed inset-0 z-50 flex items-center justify-center bg-black/30 ios-blur",
            ),
        )
    )


def usuarios_page() -> rx.Component:
    return rx.el.div(
        user_modal(),
        delete_confirmation_dialog(),
        rx.el.div(
            rx.el.h2("Gestión de Usuarios", class_name="text-2xl text-foreground"),
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground",
                    ),
                    rx.el.input(
                        placeholder="Buscar por usuario o descripción...",
                        on_change=UsuariosState.set_search_query,
                        class_name="pl-9 pr-4 py-2 w-full md:w-64 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring transition-smooth",
                    ),
                    class_name="relative",
                ),
                rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        checked=UsuariosState.show_inactive,
                        on_change=UsuariosState.set_show_inactive,
                        class_name="h-4 w-4 rounded border-input text-primary focus:ring-ring",
                    ),
                    rx.el.span(
                        "Mostrar inactivos",
                        class_name="ml-2 text-sm font-medium text-foreground",
                    ),
                    class_name="flex items-center cursor-pointer select-none whitespace-nowrap",
                ),
                rx.el.button(
                    rx.icon("circle_plus", class_name="h-5 w-5 mr-2"),
                    "Añadir Usuario",
                    on_click=UsuariosState.open_add_modal,
                    class_name="flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-lg shadow-md ios-hover transition-smooth whitespace-nowrap",
                ),
                class_name="flex flex-col md:flex-row items-start md:items-center gap-4",
            ),
            class_name="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Usuario",
                                class_name="px-6 py-3 text-left text-xs text-muted-foreground uppercase tracking-wider",
                            ),
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
                            UsuariosState.filtered_users,
                            lambda user: rx.el.tr(
                                rx.el.td(
                                    rx.el.span(
                                        user["name"],
                                        class_name="text-sm font-normal text-foreground",
                                    ),
                                    class_name="px-6 py-4 whitespace-nowrap",
                                ),
                                rx.el.td(
                                    user["description"],
                                    class_name="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground",
                                ),
                                rx.el.td(
                                    rx.el.span(
                                        rx.cond(user["active"], "Activo", "Inactivo"),
                                        class_name=rx.cond(
                                            user["active"],
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
                                        on_click=lambda: UsuariosState.open_edit_modal(
                                            user
                                        ),
                                        class_name="p-2 hover:bg-accent rounded-full transition-smooth",
                                    ),
                                    rx.el.button(
                                        rx.icon(
                                            "trash-2",
                                            class_name="h-5 w-5 text-destructive",
                                        ),
                                        on_click=lambda: UsuariosState.confirm_delete_user(
                                            user
                                        ),
                                        class_name="p-2 hover:bg-accent rounded-full transition-smooth",
                                    ),
                                    class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium",
                                ),
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
        on_mount=UsuariosState.load_users,
    )