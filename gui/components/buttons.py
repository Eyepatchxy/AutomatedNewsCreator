from nicegui import ui

def back_button(target: str) -> None:
    ui.button("Back", icon="arrow_back", on_click=lambda: ui.navigate.to(target)).props(
        "flat color=grey-8"
    )

def nav_button(label: str, target: str, icon: str, active: bool = False) -> None:
    color = "primary" if active else "grey-7"
    ui.button(label, icon=icon, on_click=lambda: ui.navigate.to(target)).props(
        f"flat color={color}"
    )