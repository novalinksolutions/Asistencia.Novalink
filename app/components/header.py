import reflex as rx
from app.states.base_state import BaseState
from app.states.header_state import HeaderState


def password_change_modal() -> rx.Component:
    return rx.cond(
        HeaderState.show_password_modal | BaseState.force_password_change_on_login,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Cambiar Contraseña", class_name="text-lg text-card-foreground"
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-5 w-5 text-muted-foreground"),
                        on_click=HeaderState.close_password_modal,
                        class_name="p-1 rounded-full ios-hover hover:bg-muted transition-colors",
                    ),
                    class_name="flex justify-between items-center pb-4 border-b",
                ),
                rx.cond(
                    BaseState.password_expired_message != "",
                    rx.el.div(
                        rx.icon(
                            "circle-alert", class_name="h-5 w-5 text-amber-600 shrink-0"
                        ),
                        rx.el.p(
                            BaseState.password_expired_message,
                            class_name="text-sm text-amber-800 ml-2",
                        ),
                        class_name="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-center",
                    ),
                    None,
                ),
                rx.el.div(
                    rx.el.label(
                        "Contraseña Actual", class_name="text-sm text-muted-foreground"
                    ),
                    rx.el.input(
                        type="password",
                        on_change=HeaderState.set_current_password,
                        class_name="mt-1 w-full px-5 py-2 rounded-lg border-input bg-background shadow-sm focus:ring-2 focus:ring-ring transition-smooth mb-4",
                        default_value=HeaderState.current_password,
                    ),
                    rx.el.label(
                        "Nueva Contraseña", class_name="text-sm text-muted-foreground"
                    ),
                    rx.el.input(
                        type="password",
                        on_change=HeaderState.set_new_password,
                        class_name="mt-1 w-full px-5 py-2 rounded-lg border-input bg-background shadow-sm focus:ring-2 focus:ring-ring transition-smooth mb-4",
                        default_value=HeaderState.new_password,
                    ),
                    rx.el.label(
                        "Confirmar Nueva Contraseña",
                        class_name="text-sm text-muted-foreground",
                    ),
                    rx.el.input(
                        type="password",
                        on_change=HeaderState.set_confirm_password,
                        class_name="mt-1 w-full px-5 py-2 rounded-lg border-input bg-background shadow-sm focus:ring-2 focus:ring-ring transition-smooth",
                        default_value=HeaderState.confirm_password,
                    ),
                    class_name="py-4",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancelar",
                        on_click=HeaderState.close_password_modal,
                        class_name="px-4 py-2 bg-button-inactive text-button-inactive-foreground rounded-lg border border-button-inactive-border transition-smooth ios-hover",
                    ),
                    rx.el.button(
                        rx.cond(
                            HeaderState.is_loading,
                            rx.el.div(
                                class_name="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"
                            ),
                            "Actualizar Contraseña",
                        ),
                        on_click=HeaderState.change_password,
                        disabled=HeaderState.is_loading,
                        class_name="px-4 py-2 bg-primary text-primary-foreground rounded-lg ml-3 transition-smooth ios-hover flex items-center gap-2",
                    ),
                    class_name="flex justify-end pt-4 border-t",
                ),
                class_name="bg-card rounded-xl shadow-2xl p-6 w-full max-w-md relative z-[101] animate-in zoom-in-95 duration-200 border border-border pointer-events-auto",
            ),
            class_name="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200 pointer-events-none",
        ),
    )


def user_dropdown() -> rx.Component:
    return rx.cond(
        HeaderState.show_dropdown,
        rx.el.div(
            rx.el.button(
                rx.icon("key-round", class_name="h-4 w-4 mr-3 text-muted-foreground"),
                "Cambiar Contraseña",
                on_click=HeaderState.open_password_modal,
                class_name="flex items-center w-full px-4 py-2 text-sm text-foreground hover:bg-muted transition-colors text-left",
            ),
            rx.el.button(
                rx.icon("log-out", class_name="h-4 w-4 mr-3 text-destructive"),
                "Cerrar Sesión",
                on_click=HeaderState.logout,
                class_name="flex items-center w-full px-4 py-2 text-sm text-destructive hover:bg-red-50 transition-colors text-left border-t",
            ),
            class_name="absolute right-0 top-full mt-2 w-56 bg-card rounded-xl shadow-xl border border-border py-1 z-40 animate-in fade-in zoom-in-95 duration-200",
        ),
    )


def header() -> rx.Component:
    return rx.fragment(
        password_change_modal(),
        rx.el.header(
            rx.el.div(
                rx.el.button(
                    rx.icon("menu", class_name="h-5 w-5 text-muted-foreground"),
                    on_click=BaseState.toggle_sidebar,
                    class_name="p-1.5 rounded-full ios-hover",
                ),
                class_name="flex-1 flex justify-start",
            ),
            rx.el.div(
                rx.cond(
                    BaseState.current_company_name != "",
                    rx.el.div(
                        rx.icon("building-2", class_name="h-3.5 w-3.5 text-primary"),
                        rx.el.span(
                            BaseState.current_company_name,
                            class_name="text-sm font-medium text-foreground truncate max-w-[200px] md:max-w-[300px]",
                        ),
                        class_name="flex items-center gap-1.5 justify-center px-3 py-1.5 bg-muted/30 rounded-md",
                    ),
                ),
                class_name="flex-1 flex justify-center items-center",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.button(
                        rx.el.div(
                            rx.el.div(
                                rx.el.p(
                                    BaseState.logged_user_name,
                                    class_name="text-xs text-foreground truncate max-w-[150px]",
                                ),
                                rx.el.p(
                                    BaseState.logged_user_description,
                                    class_name="text-[10px] text-muted-foreground truncate max-w-[150px]",
                                ),
                                class_name="flex flex-col text-right hidden sm:flex",
                            ),
                            rx.image(
                                src=f"https://api.dicebear.com/9.x/initials/svg?seed={BaseState.user_initials}&backgroundColor=000000&textColor=ffffff",
                                class_name="h-8 w-8 rounded-full border-2 border-card shrink-0",
                            ),
                            rx.icon(
                                "chevron-down",
                                class_name="h-3.5 w-3.5 text-muted-foreground shrink-0",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        on_click=HeaderState.toggle_dropdown,
                        class_name="flex items-center gap-2 hover:bg-muted/50 p-1 rounded-lg transition-colors",
                    ),
                    user_dropdown(),
                    class_name="relative",
                ),
                class_name="flex-1 flex items-center justify-end gap-2",
            ),
            class_name="flex items-center h-14 px-4 bg-card/95 border-b sticky top-0 z-10 shadow-sm ios-blur",
        ),
    )