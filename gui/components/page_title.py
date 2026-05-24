from nicegui import ui


def page_title(title: str, subtitle: str | None = None) -> None:
    with ui.column().classes("gap-1"):
        ui.label(title).classes("text-3xl font-bold tracking-tight")
        if subtitle:
            ui.label(subtitle).classes("muted text-base")