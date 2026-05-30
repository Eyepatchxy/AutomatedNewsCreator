from nicegui import ui
from gui.components.page_shell import page_shell
from gui.components.cards import action_card
from gui.components.content import content
from tasks.authorization import authorize
from gui.routes import get_path


@ui.page(get_path("Home"))
def home_page() -> None:
    page_shell("home")
    with content():
        with ui.column().classes("min-h-[70vh] w-full items-center justify-center gap-8"):
            ui.label("Automated News Creator").classes(
                "text-center text-5xl font-bold tracking-tight"
            )
            with ui.row().classes("w-full justify-end"):
                ui.button(
                    "Renew Youtube Token",
                    icon="token",
                    on_click=lambda: authorize(
                        on_success=lambda: ui.notify(
                            "YouTube token renewed successfully",
                            type="positive",
                        ),
                        on_error=lambda e: ui.notify(
                            f"Authorization failed: {e}",
                            type="negative",
                        ),
                    ),
                ).props("color=primary")

            with ui.row().classes("w-full max-w-4xl gap-5"):
                action_card(
                    "Generate Using YT Channels",
                    "Fetch, verify, cluster, and turn channel news into videos.",
                    "smart_display",
                    get_path("Channel-wise Workflow"),
                )
                action_card(
                    "Generate Using Custom Topic",
                    "Start with your own topic and move straight into video creation.",
                    "topic",
                    get_path("Topic-wise Workflow"),
                )