from nicegui import ui

def action_card(title: str, subtitle: str, icon: str, target: str) -> None:
    with ui.card().classes("surface action-card p-6 flex-1").on(
        "click", lambda: ui.navigate.to(target)
    ):
        ui.icon(icon).classes("text-4xl text-primary")
        ui.label(title).classes("text-xl font-semibold")
        ui.label(subtitle).classes("muted text-sm leading-6")

def stat_card(label: str, value: str, icon: str) -> None:
    with ui.card().classes("surface p-5 flex-1"):
        with ui.row().classes("items-center gap-3"):
            ui.icon(icon).classes("text-2xl text-primary")
            with ui.column().classes("gap-0"):
                ui.label(value).classes("text-2xl font-bold")
                ui.label(label).classes("muted text-sm")