import reflex as rx
from app.states.base_state import BaseState, NavItem


def sidebar_submenu_item(item: NavItem) -> rx.Component:
    display_text = rx.cond(item.label != "", item.label, item.name)
    return rx.el.div(
        rx.icon(item.icon, class_name="h-4 w-4 shrink-0"),
        rx.cond(
            ~BaseState.sidebar_collapsed,
            rx.el.span(display_text, class_name="truncate text-xs"),
            None,
        ),
        on_click=lambda: BaseState.set_active_page(item.name),
        class_name=rx.cond(
            BaseState.active_page == item.name,
            "flex items-center gap-2 rounded-lg border bg-sidebar-accent px-3 py-1.5 text-sidebar-accent-foreground transition-smooth border-primary cursor-pointer",
            "flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-1.5 text-muted-foreground transition-smooth hover:bg-accent hover:text-accent-foreground hover:border-accent-foreground/50 cursor-pointer",
        ),
    )


def sidebar_module(module: NavItem) -> rx.Component:
    is_expanded = BaseState.expanded_modules.get(module.name, False)
    return rx.el.div(
        rx.el.button(
            rx.icon(module.icon, class_name="h-4 w-4 shrink-0"),
            rx.cond(
                ~BaseState.sidebar_collapsed,
                rx.el.span(module.name, class_name="truncate text-xs font-medium"),
                None,
            ),
            rx.cond(
                ~BaseState.sidebar_collapsed & (module.sub_items.length() > 0),
                rx.icon(
                    "chevron-down",
                    class_name=rx.cond(
                        is_expanded,
                        "h-3 w-3 ml-auto transition-smooth",
                        "h-3 w-3 ml-auto transition-smooth rotate-[-90deg]",
                    ),
                ),
                None,
            ),
            on_click=lambda: BaseState.toggle_module(module.name),
            class_name=rx.cond(
                is_expanded,
                "flex items-center w-full gap-2 rounded-lg px-3 py-2 text-primary-foreground bg-primary transition-smooth",
                "flex items-center w-full gap-2 rounded-lg px-3 py-2 text-foreground bg-card hover:bg-muted transition-smooth",
            ),
        ),
        rx.cond(
            ~BaseState.sidebar_collapsed & is_expanded,
            rx.el.div(
                rx.foreach(module.sub_items, sidebar_submenu_item),
                class_name=rx.cond(
                    is_expanded,
                    "grid gap-0.5 transition-smooth grid-rows-[1fr] opacity-100 pt-1 pl-4 overflow-hidden",
                    "grid gap-0.5 transition-smooth grid-rows-[0fr] opacity-0 pt-0 pl-4 overflow-hidden",
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
                        src="/placeholder.svg", class_name="h-8 w-auto logo-filter"
                    ),
                    rx.image(
                        src="/placeholder.svg", class_name="h-8 w-auto logo-filter"
                    ),
                ),
                class_name="flex items-center justify-center h-12 px-3 border-b",
            ),
            rx.el.nav(
                rx.cond(
                    ~BaseState.sidebar_collapsed,
                    rx.el.h3(
                        "Menú Principal",
                        class_name="px-3 pt-2 pb-1 text-[10px] uppercase tracking-wider text-muted-foreground",
                    ),
                    None,
                ),
                rx.foreach(BaseState.navigation_menu, sidebar_module),
                class_name="flex-1 overflow-auto py-2 px-2 space-y-1 flex flex-col custom-scrollbar",
            ),
        ),
        class_name=rx.cond(
            BaseState.sidebar_collapsed,
            "flex flex-col h-screen bg-sidebar-background/95 text-sidebar-foreground border-r border-sidebar-border shadow-lg transition-smooth w-[60px] ios-blur shrink-0",
            "flex flex-col h-screen bg-sidebar-background/95 text-sidebar-foreground border-r border-sidebar-border shadow-lg transition-smooth w-60 md:w-64 ios-blur shrink-0",
        ),
    )