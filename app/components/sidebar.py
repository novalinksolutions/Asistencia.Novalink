import reflex as rx
from app.states.base_state import BaseState, NavItem


def sidebar_submenu_item(item: NavItem) -> rx.Component:
    display_text = rx.cond(item.label != "", item.label, item.name)
    return rx.el.div(
        rx.icon(item.icon, class_name="h-5 w-5 shrink-0"),
        rx.cond(
            ~BaseState.sidebar_collapsed,
            rx.el.span(display_text, class_name="truncate"),
            None,
        ),
        on_click=lambda: BaseState.set_active_page(item.name),
        class_name=rx.cond(
            BaseState.active_page == item.name,
            "flex items-center gap-3 rounded-lg border bg-sidebar-accent px-3 py-2.5 text-sidebar-accent-foreground transition-smooth border-primary cursor-pointer",
            "flex items-center gap-3 rounded-lg border border-border bg-card px-3 py-2.5 text-muted-foreground transition-smooth hover:bg-accent hover:text-accent-foreground hover:border-accent-foreground/50 cursor-pointer",
        ),
    )


def sidebar_module(module: NavItem) -> rx.Component:
    is_expanded = BaseState.expanded_modules.get(module.name, False)
    is_active_module = BaseState.active_module_name == module.name
    return rx.el.div(
        rx.el.button(
            rx.icon(module.icon, class_name="h-5 w-5 shrink-0"),
            rx.cond(
                ~BaseState.sidebar_collapsed,
                rx.el.span(module.name, class_name="truncate"),
                None,
            ),
            rx.cond(
                ~BaseState.sidebar_collapsed & (module.sub_items.length() > 0),
                rx.icon(
                    "chevron-down",
                    class_name=rx.cond(
                        is_expanded,
                        "h-5 w-5 ml-auto transition-smooth",
                        "h-5 w-5 ml-auto transition-smooth rotate-[-90deg]",
                    ),
                ),
                None,
            ),
            on_click=lambda: BaseState.toggle_module(module.name),
            class_name=rx.cond(
                is_expanded,
                "flex items-center w-full gap-3 rounded-lg px-4 py-3 text-primary-foreground bg-primary transition-smooth",
                "flex items-center w-full gap-3 rounded-lg px-4 py-3 text-foreground bg-card hover:bg-muted transition-smooth",
            ),
        ),
        rx.cond(
            ~BaseState.sidebar_collapsed & is_expanded,
            rx.el.div(
                rx.foreach(module.sub_items, sidebar_submenu_item),
                class_name=rx.cond(
                    is_expanded,
                    "grid gap-1 transition-smooth grid-rows-[1fr] opacity-100 pt-2 pl-4 overflow-hidden",
                    "grid gap-1 transition-smooth grid-rows-[0fr] opacity-0 pt-0 pl-4 overflow-hidden",
                ),
            ),
            None,
        ),
        class_name="flex flex-col",
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.cond(
                    BaseState.sidebar_collapsed,
                    rx.image(
                        src="/placeholder.svg", class_name="h-12 w-auto logo-filter"
                    ),
                    rx.image(
                        src="/placeholder.svg", class_name="h-12 w-auto logo-filter"
                    ),
                ),
                class_name="flex items-center justify-center h-16 px-4 border-b",
            ),
            rx.el.nav(
                rx.cond(
                    ~BaseState.sidebar_collapsed,
                    rx.el.h3(
                        "Menú Principal",
                        class_name="px-4 pt-4 pb-2 text-sm tracking-wider text-muted-foreground",
                    ),
                    None,
                ),
                rx.foreach(BaseState.navigation_menu, sidebar_module),
                class_name="flex-1 overflow-auto py-2 px-4 space-y-2 flex flex-col",
            ),
        ),
        class_name=rx.cond(
            BaseState.sidebar_collapsed,
            "flex flex-col h-screen bg-sidebar-background/95 text-sidebar-foreground border-r border-sidebar-border shadow-lg transition-smooth w-[72px] ios-blur",
            "flex flex-col h-screen bg-sidebar-background/95 text-sidebar-foreground border-r border-sidebar-border shadow-lg transition-smooth w-72 md:w-[288px] ios-blur",
        ),
    )