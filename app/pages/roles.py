import reflex as rx
from app.states.roles_state import RolesState, Permission


def permission_checkbox(permission: Permission) -> rx.Component:
    is_checked = RolesState.modal_role["permissions"].contains(permission["id"])
    return rx.el.label(
        rx.el.input(
            type="checkbox",
            on_change=lambda: RolesState.toggle_permission(permission["id"]),
            checked=is_checked,
            class_name="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
        ),
        rx.el.span(permission["name"], class_name="ml-2 text-sm text-gray-700"),
        class_name="flex items-center p-2 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer",
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
                            class_name="text-lg font-bold text-gray-900",
                        ),
                        rx.el.button(
                            rx.icon(
                                "x",
                                class_name="h-5 w-5 text-gray-500 hover:text-gray-700",
                            ),
                            on_click=RolesState.close_modal,
                            class_name="p-1 rounded-full ios-hover",
                        ),
                        class_name="flex justify-between items-center pb-4 border-b",
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.div(
                                rx.el.label(
                                    "Nombre del Rol",
                                    class_name="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1",
                                ),
                                rx.el.input(
                                    name="name",
                                    default_value=RolesState.modal_role["name"],
                                    placeholder="Ej: Editor de Contenido",
                                    class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white",
                                ),
                                class_name="mb-3",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Descripción",
                                    class_name="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1",
                                ),
                                rx.el.textarea(
                                    name="description",
                                    default_value=RolesState.modal_role["description"],
                                    placeholder="Descripción breve del rol...",
                                    class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white",
                                    rows="2",
                                ),
                                class_name="mb-4",
                            ),
                            rx.el.h4(
                                "Permisos",
                                class_name="text-sm font-semibold text-gray-900 mb-2",
                            ),
                            rx.el.div(
                                rx.foreach(
                                    RolesState.all_permissions, permission_checkbox
                                ),
                                class_name="grid grid-cols-2 gap-2 p-3 border border-gray-200 rounded-lg bg-gray-50 max-h-48 overflow-y-auto custom-scrollbar",
                            ),
                            class_name="py-4",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Cancelar",
                                on_click=RolesState.close_modal,
                                class_name="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors",
                            ),
                            rx.el.button(
                                "Guardar",
                                type="submit",
                                class_name="flex items-center px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm ml-3",
                            ),
                            class_name="flex justify-end pt-4 border-t",
                        ),
                        on_submit=RolesState.handle_submit,
                    ),
                    class_name="bg-white rounded-xl shadow-xl p-5 w-full max-w-lg",
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
            rx.el.h2("Roles y Permisos", class_name="text-2xl text-foreground"),
            rx.el.button(
                rx.icon("circle_plus", class_name="h-5 w-5 mr-2"),
                "Añadir Rol",
                on_click=RolesState.open_add_modal,
                class_name="flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-lg shadow-md ios-hover transition-smooth",
            ),
            class_name="flex justify-between items-center mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Nombre del Rol",
                                class_name="px-6 py-3 text-left text-xs text-muted-foreground uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Descripción",
                                class_name="px-6 py-3 text-left text-xs text-muted-foreground uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Permisos",
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
                            RolesState.roles,
                            lambda role: rx.el.tr(
                                rx.el.td(
                                    role["name"],
                                    class_name="px-6 py-4 whitespace-nowrap text-sm text-foreground",
                                ),
                                rx.el.td(
                                    role["description"],
                                    class_name="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground max-w-xs truncate",
                                ),
                                rx.el.td(
                                    rx.el.span(
                                        role["permissions"].length().to_string(),
                                        class_name="px-2.5 py-1 text-xs rounded-full bg-primary/10 text-primary",
                                    ),
                                    class_name="px-6 py-4 whitespace-nowrap text-sm",
                                ),
                                rx.el.td(
                                    rx.el.button(
                                        rx.icon(
                                            "copy", class_name="h-5 w-5 text-primary"
                                        ),
                                        on_click=lambda: RolesState.open_edit_modal(
                                            role
                                        ),
                                        class_name="p-2 hover:bg-accent rounded-full transition-smooth",
                                    ),
                                    rx.el.button(
                                        rx.icon(
                                            "trash-2",
                                            class_name="h-5 w-5 text-destructive",
                                        ),
                                        on_click=lambda: RolesState.confirm_delete_role(
                                            role
                                        ),
                                        class_name="p-2 hover:bg-accent rounded-full transition-smooth",
                                    ),
                                    class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2",
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