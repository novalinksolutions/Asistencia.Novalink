import reflex as rx
from app.states.login_state import LoginState


def login_form_field(
    label: str, name: str, placeholder: str, type: str, icon: str
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label, html_for=name, class_name="text-sm text-gray-700 ml-1 mb-1.5"
        ),
        rx.el.div(
            rx.icon(
                icon,
                class_name="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-400",
            ),
            rx.el.input(
                id=name,
                name=name,
                placeholder=placeholder,
                type=type,
                class_name="w-full h-10 pl-9 pr-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 text-sm transition-all duration-200",
            ),
            class_name="relative w-full",
        ),
        class_name="flex flex-col w-full",
    )


def company_selector() -> rx.Component:
    return rx.el.div(
        rx.el.label("Empresa", class_name="text-[15px] text-gray-700 ml-1 mb-2"),
        rx.el.div(
            rx.cond(
                LoginState.empresa != "",
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "building-2", class_name="h-4 w-4 text-blue-600 shrink-0"
                        ),
                        class_name="flex items-center justify-center w-8 h-8 rounded-lg bg-blue-50 mr-3",
                    ),
                    rx.el.div(
                        rx.el.span(
                            LoginState.search_text,
                            class_name="block text-[15px] text-gray-900 truncate",
                        ),
                        class_name="flex-1 min-w-0 flex flex-col justify-center",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4 text-gray-400"),
                        type="button",
                        on_click=LoginState.clear_company_selection,
                        class_name="p-1.5 hover:bg-gray-100 rounded-full transition-colors shrink-0 ml-2",
                        title="Cambiar empresa",
                    ),
                    class_name="w-full h-auto min-h-[2.75rem] p-2 pl-3 flex items-center bg-white border border-blue-200/60 ring-4 ring-blue-50/50 rounded-xl shadow-sm transition-all",
                ),
                rx.el.div(
                    rx.icon(
                        "building-2",
                        class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400",
                    ),
                    rx.el.input(
                        type="text",
                        on_change=LoginState.set_search_text_change,
                        placeholder="Buscar empresa...",
                        class_name="w-full h-11 pl-10 pr-4 bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 text-[15px] transition-all duration-200",
                        default_value=LoginState.search_text,
                    ),
                    rx.el.div(
                        rx.cond(
                            LoginState.filtered_companies.length() > 0,
                            rx.foreach(
                                LoginState.filtered_companies,
                                lambda c: rx.el.div(
                                    rx.el.span(
                                        c["name"],
                                        class_name="text-[15px] text-gray-900",
                                    ),
                                    on_click=lambda: LoginState.select_company(
                                        c["id"], c["name"]
                                    ),
                                    class_name="px-5 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-0 flex items-center transition-colors",
                                ),
                            ),
                            rx.el.div(
                                "No se encontraron empresas",
                                class_name="px-5 py-3 text-[15px] text-gray-500 italic text-center",
                            ),
                        ),
                        class_name=rx.cond(
                            LoginState.show_suggestions,
                            "absolute top-full left-0 right-0 mt-2 bg-white border border-gray-100 rounded-xl shadow-2xl max-h-[300px] overflow-y-auto z-50 animate-in fade-in zoom-in-95 duration-200",
                            "hidden",
                        ),
                    ),
                    class_name="relative w-full",
                ),
            )
        ),
        class_name="flex flex-col w-full",
    )


def login_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.image(
                    src="/placeholder.svg",
                    class_name="h-24 md:h-32 w-auto logo-filter hover:scale-105 transition-transform duration-500",
                ),
                class_name="flex flex-col justify-center items-center w-full h-48 md:h-auto bg-blue-50/30 p-8 border-b border-gray-200 md:border-b-0 md:border-r relative z-10 md:shadow-[4px_0_20px_-4px_rgba(0,0,0,0.08)]",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.h1("Bienvenido", class_name="text-xl text-gray-900"),
                    rx.el.p(
                        "Inicia sesión para continuar",
                        class_name="text-gray-500 text-sm mt-1 mb-6",
                    ),
                    rx.el.form(
                        rx.el.input(
                            type="hidden", name="empresa", value=LoginState.empresa
                        ),
                        rx.el.div(
                            company_selector(),
                            login_form_field(
                                "Usuario",
                                "username",
                                "Ingresa tu usuario",
                                "text",
                                "user",
                            ),
                            login_form_field(
                                "Contraseña", "password", "••••••••", "password", "lock"
                            ),
                            class_name="flex flex-col gap-4 w-full mb-6",
                        ),
                        rx.el.div(
                            rx.el.button(
                                rx.cond(
                                    LoginState.is_loading,
                                    rx.el.div(
                                        class_name="animate-spin rounded-full h-3.5 w-3.5 border-2 border-white border-t-transparent"
                                    ),
                                    rx.el.span("Iniciar Sesión", class_name="text-sm"),
                                ),
                                type="submit",
                                disabled=LoginState.is_loading,
                                class_name="w-full h-10 flex justify-center items-center bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg hover:shadow-blue-500/30 transition-all duration-300 active:scale-[0.98]",
                            ),
                            class_name="flex justify-center w-full",
                        ),
                        on_submit=LoginState.handle_login,
                        reset_on_submit=True,
                        class_name="w-full",
                    ),
                    rx.cond(
                        LoginState.error_message != "",
                        rx.el.div(
                            rx.icon(
                                "circle-alert",
                                class_name="h-4 w-4 text-red-600 shrink-0",
                            ),
                            rx.el.p(
                                LoginState.error_message,
                                class_name="text-[13px] text-red-600 ml-2",
                            ),
                            class_name="mt-4 p-3 bg-red-50 border border-red-100 rounded-xl flex items-center justify-center animate-in slide-in-from-bottom-2 fade-in duration-300",
                        ),
                    ),
                    class_name="w-full max-w-md mx-auto flex flex-col justify-center h-full",
                ),
                class_name="p-8 md:p-12 w-full h-full flex flex-col justify-center bg-white",
            ),
            class_name="grid md:grid-cols-2 w-full max-w-5xl bg-white backdrop-blur-xl rounded-[2.5rem] shadow-2xl overflow-hidden border border-white/20 ring-1 ring-black/5 min-h-[600px] animate-fade-in-up",
        ),
        class_name="min-h-screen w-full flex items-center justify-center bg-gray-50/50 p-4 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-50 via-gray-50 to-gray-100",
    )