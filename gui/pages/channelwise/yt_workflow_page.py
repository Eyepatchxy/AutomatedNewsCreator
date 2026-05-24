from nicegui import ui
from gui.components.page_title import page_title
from gui.components.content import content
from gui.components.page_shell import page_shell
from gui.components.buttons import back_button
from gui.components.cards import action_card
from gui.routes import get_path

@ui.page(get_path("Channel-wise Workflow"))
def yt_workflow_page() -> None:
    page_shell(get_path("Channel-wise Workflow"))
    with content():
        back_button(get_path("Home"))
        page_title("YT Workflow", "Choose whether to process channel news or create videos from processed stories.")
        with ui.row().classes("w-full gap-5"):
            action_card(
                "Fetch & Process News",
                "Select channels first, then confirm before extraction begins.",
                "travel_explore",
                get_path("Channel Selection"),
            )
            action_card(
                "Generate Videos From Processed News",
                "Pick a processed story and configure the video output.",
                "movie_creation",
                get_path("Processed News"),
            )
            action_card(
                "Upload Generated Videos",
                "Publish rendered videos that have not been uploaded yet.",
                "cloud_upload",
                get_path("Upload Generated Videos"),
            )
