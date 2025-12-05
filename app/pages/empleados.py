import reflex as rx


def empleados_page() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Empleados", class_name="text-2xl font-bold text-gray-900 mb-4"),
        rx.el.div(
            rx.icon("hammer", class_name="h-12 w-12 text-gray-400 mb-4"),
            rx.el.p(
                "El módulo de Empleados se encuentra actualmente en desarrollo.",
                class_name="text-lg text-gray-600 font-medium",
            ),
            rx.el.p(
                "Próximamente podrá gestionar los empleados desde esta pantalla.",
                class_name="text-sm text-gray-500 mt-2",
            ),
            class_name="flex flex-col items-center justify-center p-12 bg-white rounded-xl shadow-sm border border-gray-200",
        ),
        class_name="animate-fade-in-up",
    )