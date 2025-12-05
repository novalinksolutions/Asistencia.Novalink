import reflex as rx
from app.components.base_layout import base_layout
from app.states.base_state import BaseState
from app.pages.parametros_generales import parametros_generales_page
from app.pages.tipo_justificaciones import tipo_justificaciones_page
from app.pages.definir_feriados import definir_feriados_page
from app.pages.usuarios import usuarios_page
from app.pages.roles import roles_page
from app.pages.catalogo_nivel1 import catalogo_nivel1_page
from app.pages.catalogo_nivel2 import catalogo_nivel2_page
from app.pages.catalogo_nivel3 import catalogo_nivel3_page
from app.pages.catalogo_nivel4 import catalogo_nivel4_page
from app.pages.catalogo_nivel5 import catalogo_nivel5_page
from app.pages.entidades import entidades_page
from app.pages.empleados import empleados_page
from app.pages.login import login_page
from app.states.login_state import LoginState
from app.utils.assets import ensure_assets


def index() -> rx.Component:
    return base_layout(
        rx.match(
            BaseState.active_page,
            ("Parámetros Generales", parametros_generales_page()),
            ("Tipo de Justificaciones", tipo_justificaciones_page()),
            ("Definir Feriados", definir_feriados_page()),
            ("Usuarios", usuarios_page()),
            ("Roles", roles_page()),
            ("Nivel 1", catalogo_nivel1_page()),
            ("Nivel 2", catalogo_nivel2_page()),
            ("Nivel 3", catalogo_nivel3_page()),
            ("Nivel 4", catalogo_nivel4_page()),
            ("Nivel 5", catalogo_nivel5_page()),
            ("Entidades", entidades_page()),
            ("Empleados", empleados_page()),
            rx.el.div(
                rx.el.h2(
                    "Bienvenido al Panel de Administración",
                    class_name="text-2xl font-bold text-gray-800 mb-4",
                ),
                rx.el.p(
                    f"Página activa: {BaseState.active_page}",
                    class_name="text-gray-600",
                ),
                rx.el.div(
                    rx.el.p(
                        "Seleccione una opción del menú lateral para comenzar.",
                        class_name="text-gray-500",
                    ),
                    class_name="mt-8 p-8 bg-white rounded-lg border border-gray-200 shadow-sm",
                ),
                class_name="animate-fade-in-up",
            ),
        )
    )


ensure_assets()
app = rx.App(
    theme=rx.theme(appearance="light", radius="large", accent_color="blue"),
    stylesheets=["/styles.css"],
    head_components=[
        rx.el.style("""
            @keyframes fade-in-up {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            .animate-fade-in-up {
                animation: fade-in-up 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            }
            """)
    ],
)
app.add_page(index, route="/", on_load=BaseState.check_login)
app.add_page(login_page, route="/login", on_load=LoginState.on_load)