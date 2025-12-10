import reflex as rx
from app.components.sidebar import sidebar
from app.components.header import header


def base_layout(content: rx.Component) -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            header(),
            rx.el.main(
                content, class_name="flex-1 p-3 md:p-4 bg-background overflow-hidden"
            ),
            class_name="flex flex-col flex-1 h-screen overflow-hidden",
        ),
        class_name="flex h-screen w-full bg-background overflow-hidden",
    )