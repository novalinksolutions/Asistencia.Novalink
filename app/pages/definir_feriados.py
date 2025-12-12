import reflex as rx
from app.states.definir_feriados_state import DefinirFeriadosState, Month, Day


def legend_item(color: str, text: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(class_name=f"w-4 h-4 rounded-sm {color}"),
        rx.el.span(text, class_name="text-sm text-muted-foreground"),
        class_name="flex items-center gap-2",
    )


def calendar_day(day: Day) -> rx.Component:
    holiday_type = DefinirFeriadosState.holidays.get(day["date_str"], "")
    is_readonly = DefinirFeriadosState.readonly_holidays.contains(day["date_str"])
    return rx.el.button(
        day["day_num"],
        on_click=lambda: DefinirFeriadosState.toggle_holiday(day["date_str"]),
        class_name=rx.cond(
            day["is_current_month"],
            rx.cond(
                is_readonly,
                "w-8 h-8 flex items-center justify-center rounded-lg bg-gray-400 text-white cursor-not-allowed",
                rx.match(
                    holiday_type,
                    (
                        "descanso_obligatorio",
                        "w-8 h-8 flex items-center justify-center rounded-lg bg-blue-500 text-white text-sm transition-smooth hover:bg-blue-600",
                    ),
                    (
                        "feriado_recuperable",
                        "w-8 h-8 flex items-center justify-center rounded-lg bg-green-500 text-white text-sm transition-smooth hover:bg-green-600",
                    ),
                    (
                        "jornada_recuperacion",
                        "w-8 h-8 flex items-center justify-center rounded-lg bg-red-500 text-white text-sm transition-smooth hover:bg-red-600",
                    ),
                    "w-8 h-8 flex items-center justify-center rounded-lg text-foreground text-sm transition-smooth hover:bg-accent",
                ),
            ),
            "w-8 h-8 flex items-center justify-center rounded-lg text-muted-foreground/50 text-sm transition-smooth hover:bg-accent",
        ),
        disabled=~day["is_current_month"] | is_readonly,
    )


def month_view(month: Month) -> rx.Component:
    days_of_week = ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa"]
    return rx.el.div(
        rx.el.h3(
            month["month_name"], class_name="text-center text-foreground mb-2 text-base"
        ),
        rx.el.div(
            rx.foreach(
                days_of_week,
                lambda day: rx.el.div(
                    day,
                    class_name="text-center text-xs font-medium text-muted-foreground",
                ),
            ),
            class_name="grid grid-cols-7 gap-y-1 mb-2",
        ),
        rx.el.div(
            rx.foreach(
                month["weeks"],
                lambda week: rx.el.div(
                    rx.foreach(week, calendar_day),
                    class_name="grid grid-cols-7 gap-y-0.5",
                ),
            ),
            class_name="space-y-0.5",
        ),
        class_name="bg-card p-3 rounded-xl border shadow-sm",
    )


def definir_feriados_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Definir Feriados", class_name="text-2xl text-foreground text-center"
            ),
            rx.el.div(
                legend_item("bg-blue-500", "Descanso Obligatorio"),
                legend_item("bg-green-500", "Feriado Recuperable"),
                legend_item("bg-red-500", "Jornada de Recuperación"),
                class_name="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 mb-4 p-3 bg-card rounded-xl border",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.span("Año:", class_name="text-muted-foreground"),
                    rx.el.button(
                        rx.icon("chevron-left", class_name="h-5 w-5"),
                        on_click=DefinirFeriadosState.decrement_year,
                        class_name="p-2 rounded-lg ios-hover transition-smooth bg-card border",
                    ),
                    rx.el.span(
                        DefinirFeriadosState.selected_year,
                        class_name="text-lg w-12 text-center",
                    ),
                    rx.el.button(
                        rx.icon("chevron-right", class_name="h-5 w-5"),
                        on_click=DefinirFeriadosState.increment_year,
                        class_name="p-2 rounded-lg ios-hover transition-smooth bg-card border",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.cond(
                    DefinirFeriadosState.show_nivel_filter,
                    rx.el.div(
                        rx.el.span(
                            "Nivel Administrativo:",
                            class_name="text-sm text-gray-600 font-medium",
                        ),
                        rx.el.select(
                            rx.foreach(
                                DefinirFeriadosState.niveles_administrativos,
                                lambda n: rx.el.option(n["name"], value=n["id"]),
                            ),
                            on_change=DefinirFeriadosState.set_nivel_administrativo_seleccionado,
                            value=DefinirFeriadosState.nivel_administrativo_seleccionado,
                            class_name="w-full max-w-[200px] px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white text-sm",
                        ),
                        class_name="flex items-center gap-2",
                    ),
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("save", class_name="h-4 w-4 mr-2"),
                        "Guardar Feriados",
                        on_click=DefinirFeriadosState.save_holidays,
                        class_name="flex items-center px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm",
                    ),
                    class_name="flex items-center gap-3",
                ),
                class_name="flex flex-wrap items-center justify-center gap-x-6 gap-y-3 mb-4 p-3 bg-card rounded-xl border shadow-sm sticky top-20 z-10",
            ),
            rx.el.div(
                rx.foreach(DefinirFeriadosState.calendar_data, month_view),
                class_name="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3",
            ),
            class_name="w-full flex flex-col items-center space-y-4",
        ),
        class_name="animate-fade-in-up w-full flex justify-center",
    )