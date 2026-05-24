from nicegui import ui
from gui.components.page_shell import page_shell
from gui.components.page_title import page_title
from gui.components.buttons import back_button
from gui.components.content import content
from gui.components.cards import stat_card
from gui.state.app_state import STATE
from gui.services.channel_service import selected_channel_names
from gui.services.pipeline_service import prepare_extraction_job
from gui.routes import get_path

@ui.page(get_path("Extraction Confirmation"))
def extraction_confirmation_page() -> None:
    page_shell(get_path("Extraction Confirmation"))
    selected_names = selected_channel_names()
    estimated_videos = max(len(selected_names) * 12, 0)

    with content():
        back_button(get_path("Channel Selection"))
        page_title("Confirm Extraction", "Review the workload before starting the channel extraction flow.")
        with ui.row().classes("w-full gap-4"):
            stat_card("Selected Channels", str(len(selected_names)), "subscriptions")
            stat_card("Estimated Videos", str(estimated_videos), "video_library")
            stat_card("Estimated Runtime", f"{max(len(selected_names) * 3, 1)} min", "timer")

        with ui.card().classes("surface w-full p-5"):
            ui.label("Selected Channels").classes("text-lg font-semibold")
            if selected_names:
                for name in selected_names:
                    ui.label(name).classes("py-1")
            else:
                ui.label("No channels selected yet.").classes("muted")

        with ui.row().classes("w-full justify-between"):
            ui.button("Back", icon="arrow_back", on_click=lambda: ui.navigate.to(get_path("Channel Selection"))).props(
                "outline color=grey-8"
            )

            def start_extraction() -> None:
                prepare_extraction_job()
                ui.navigate.to(get_path("Extraction Progress"))

            ui.button(
                "Start Extraction",
                icon="play_arrow",
                on_click=start_extraction,
            ).props("color=primary").bind_enabled_from(STATE, "selected_channels", backward=lambda value: bool(value))
