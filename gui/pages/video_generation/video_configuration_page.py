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
from gui.state.models import VideoDuration, VideoType

def video_options_panel() -> None:

    with ui.card().classes("surface w-full p-6 gap-5"):
        ui.label("Video Configuration").classes("text-xl font-semibold")
        with ui.row():
            with ui.grid(columns=3).classes("w-full justify gap-35"):
                ui.select(
                    [VideoType.FULL, VideoType.SHORT],
                    value=STATE.get("video_type", VideoType.FULL),
                    label="Video Type",
                ).classes("w-64").bind_value(
                    STATE,
                    "video_type"
                )

                ui.select(
                    [VideoDuration.SEC_30, VideoDuration.SEC_60, VideoDuration.SEC_90, VideoDuration.SEC_120],
                    value=STATE.get("target_time", VideoDuration.SEC_90),
                    label="Target Duration",
                ).bind_value(
                    STATE,
                    "target_time"
                )

                ui.select(
                    ["News Desk", "Full Screen Visuals", "Split Layout"],
                    value="News Desk",
                    label="Background Layout",
                ).bind_value(
                    STATE,
                    "background_layout"
                )

        ui.switch(
            "Upload after generation"
        ).bind_value(
            STATE,
            "upload_job"
        )


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
        video_options_panel()

        def start_video_generation() -> None:
            prepare_video_job_from_selection()
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
