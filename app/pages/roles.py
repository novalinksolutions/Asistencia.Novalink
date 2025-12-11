import reflex as rx
from app.states.roles_state import RolesState, Permission


def permission_checkbox(permission: Permission) -> rx.Component:
    is_checked = RolesState.modal_role["permissions"].contains(permission["id"])
    return rx.el.label(
        rx.el.input(
            type="checkbox",
            on_change=lambda: RolesState.toggle_permission(permission["id"]),
            checked=is_checked,
            class_name="h-4 w-4 rounded border-input text-primary focus:ring-ring",
        ),
        rx.el.span(permission["name"], class_name="ml-2 text-sm text-foreground"),
        class_name="flex items-center p-2 rounded-md hover:bg-accent",
    )


def role_modal() -> rx.Component:
    return rx.el.div(
        rx.cond(
            RolesState.show_modal,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            rx.cond(
                                RolesState.is_editing,
                                "Editar Rol y Permisos",
                                "Añadir Nuevo Rol",
                            ),
                            class_name="text-xl text-card-foreground",
                        ),
                        rx.el.button(
                            rx.icon("x", class_name="h-5 w-5 text-muted-foreground"),
                            on_click=RolesState.close_modal,
                            class_name="p-1 rounded-full ios-hover",
                        ),
                        class_name="flex justify-between items-center pb-4 border-b",
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.label(
                                "Nombre del Rol",
                                class_name="text-sm mb-1 text-muted-foreground",
                            ),
                            rx.el.input(
                                name="name",
                                default_value=RolesState.modal_role["name"],
                                placeholder="Ej: Editor de Contenido",
                                class_name="mt-1 w-full px-5 py-2 rounded-lg border-input bg-background shadow-sm focus:ring-2 focus:ring-ring transition-smooth",
                            ),
                            rx.el.label(
                                "Descripción",
                                class_name="text-sm mt-4 mb-1 text-muted-foreground",
                            ),
                            rx.el.textarea(
                                name="description",
                                default_value=RolesState.modal_role["description"],
                                placeholder="Descripción breve del rol...",
                                class_name="mt-1 w-full px-5 py-2 rounded-lg border-input bg-background shadow-sm focus:ring-2 focus:ring-ring transition-smooth",
                            ),
                            rx.el.h4(
                                "Permisos",
                                class_name="text-md mt-6 mb-2 text-card-foreground",
                            ),
                            rx.el.div(
                                rx.foreach(
                                    RolesState.all_permissions, permission_checkbox
                                ),
                                class_name="grid grid-cols-2 gap-2 p-2 border rounded-lg bg-muted max-h-48 overflow-y-auto",
                            ),
                            class_name="py-4",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Cancelar",
                                on_click=RolesState.close_modal,
                                class_name="px-4 py-2 bg-button-inactive text-button-inactive-foreground rounded-lg border border-button-inactive-border transition-smooth ios-hover",
                            ),
                            rx.el.button(
                                "Guardar",
                                type="submit",
                                class_name="px-4 py-2 bg-primary text-primary-foreground rounded-lg ml-3 transition-smooth ios-hover",
                            ),
                            class_name="flex justify-end pt-4 border-t",
                        ),
                        on_submit=RolesState.handle_submit,
                    ),
                    class_name="bg-card rounded-xl shadow-xl p-6 w-full max-w-lg",
                ),
                class_name="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/30 animate-fade-in-up ios-blur",
            ),
        )
    )


def delete_confirmation_dialog() -> rx.Component:
    return rx.el.div(
        rx.cond(
            RolesState.show_delete_confirm,
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Confirmar Eliminación",
                        class_name="text-lg text-card-foreground",
                    ),
                    rx.el.p(
                        f"¿Está seguro de que desea eliminar el rol '{RolesState.role_to_delete['name']}'?",
                        class_name="mt-2 text-sm text-muted-foreground",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancelar",
                            on_click=RolesState.cancel_delete,
                            class_name="mt-4 px-4 py-2 bg-button-inactive text-button-inactive-foreground rounded-lg border border-button-inactive-border transition-smooth ios-hover",
                        ),
                        rx.el.button(
                            "Eliminar",
                            on_click=RolesState.delete_role,
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


def roles_page() -> rx.Component:
    return rx.el.div(
        role_modal(),
        delete_confirmation_dialog(),
        rx.el.div(
            rx.el.h2("Roles y Permisos", class_name="text-xl text-foreground"),
            rx.el.button(
                rx.icon("circle_plus", class_name="h-4 w-4 mr-2"),
                "Añadir Rol",
                on_click=RolesState.open_add_modal,
                class_name="flex items-center px-3 py-1.5 bg-primary text-primary-foreground rounded-lg shadow-md ios-hover transition-smooth text-xs",
            ),
            class_name="flex justify-between items-center mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Nombre del Rol",
                                class_name="px-4 py-2 text-left text-[10px] text-muted-foreground uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Descripción",
                                class_name="px-4 py-2 text-left text-[10px] text-muted-foreground uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Permisos",
                                class_name="px-4 py-2 text-left text-[10px] text-muted-foreground uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Acciones",
                                class_name="px-4 py-2 text-right text-[10px] text-muted-foreground uppercase tracking-wider",
                            ),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            RolesState.roles,
                            lambda role: rx.el.tr(
                                rx.el.td(
                                    role["name"],
                                    class_name="px-4 py-2 whitespace-nowrap text-xs text-foreground",
                                ),
                                rx.el.td(
                                    role["description"],
                                    class_name="px-4 py-2 whitespace-nowrap text-xs text-muted-foreground max-w-xs truncate",
                                ),
                                rx.el.td(
                                    rx.el.span(
                                        role["permissions"].length().to_string(),
                                        class_name="px-2 py-0.5 text-[10px] rounded-full bg-primary/10 text-primary",
                                    ),
                                    class_name="px-4 py-2 whitespace-nowrap text-xs",
                                ),
                                rx.el.td(
                                    rx.el.button(
                                        rx.icon(
                                            "copy", class_name="h-4 w-4 text-primary"
                                        ),
                                        on_click=lambda: RolesState.open_edit_modal(
                                            role
                                        ),
                                        class_name="p-1.5 hover:bg-accent rounded-full transition-smooth",
                                    ),
                                    rx.el.button(
                                        rx.icon(
                                            "trash-2",
                                            class_name="h-4 w-4 text-destructive",
                                        ),
                                        on_click=lambda: RolesState.confirm_delete_role(
                                            role
                                        ),
                                        class_name="p-1.5 hover:bg-accent rounded-full transition-smooth",
                                    ),
                                    class_name="px-4 py-2 whitespace-nowrap text-right text-xs font-medium space-x-1.5",
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
    )