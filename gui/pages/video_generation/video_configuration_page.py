from nicegui import ui
from gui.components.page_title import page_title
from gui.components.content import content
from gui.components.page_shell import page_shell
from gui.components.buttons import back_button
from gui.state.app_state import STATE
from gui.services.news_service import load_processed_news
from gui.services.pipeline_service import prepare_video_job_from_selection
from gui.state.models import NewsItem
from gui.routes import get_path

def video_options_panel() -> None:
    with ui.card().classes("surface w-full p-6 gap-5"):
        ui.label("Video Configuration").classes("text-xl font-semibold")
        with ui.grid(columns=3).classes("w-full gap-4"):
            ui.select(["Short", "Full"], value="Short", label="Video Type").props("outlined")
            ui.select(["30 seconds", "60 seconds", "3 minutes", "5 minutes"], value="60 seconds", label="Duration").props(
                "outlined"
            )
            ui.select(["News Desk", "Full Screen Visuals", "Split Layout"], value="News Desk", label="Background Layout").props(
                "outlined"
            )
        return ui.switch("Upload after generation", value=True)


def topic_selector_panel() -> None:
    news_items = load_processed_news()
    current = STATE.get("selected_news") or news_items[0]
    STATE["selected_news"] = current
    labels = [item.headline for item in news_items]
    if isinstance(current, NewsItem) and current.headline not in labels:
        news_items = [current, *news_items]
        labels = [item.headline for item in news_items]
    current_label = current.headline if isinstance(current, NewsItem) else labels[0]

    with ui.card().classes("surface w-full p-6 gap-3"):
        ui.label("Topic").classes("text-xl font-semibold")
        ui.select(labels, value=current_label, label="Processed topic").props("outlined").classes(
            "w-full"
        ).on_value_change(
            lambda event: STATE.update(
                {
                    "selected_news": next(
                        item for item in news_items if item.headline == event.value
                    )
                }
            )
        )
        ui.label("Best available processed topic is selected by default.").classes("muted text-sm")


@ui.page("/video/config")
def video_configuration_page() -> None:
    page_shell()
    with content():
        back_button("/yt/processed-news")
        page_title("Video Configuration", "Defaults are optimized so most runs can continue immediately.")
        topic_selector_panel()
        upload_toggle = video_options_panel()

        def start_video_generation() -> None:
            prepare_video_job_from_selection(upload=bool(upload_toggle.value))
            ui.navigate.to(get_path("Video Generation Progress"))

        with ui.row().classes("w-full justify-between"):
            ui.button("Back", icon="arrow_back", on_click=lambda: ui.navigate.back()).props(
                "outline color=grey-8"
            )
            ui.button(
                "Generate Video",
                icon="movie",
                on_click=start_video_generation,
            ).props("color=primary")
