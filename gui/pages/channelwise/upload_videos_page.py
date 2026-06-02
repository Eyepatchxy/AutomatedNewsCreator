from nicegui import run, ui

from gui.components.buttons import back_button
from gui.components.content import content
from gui.components.page_shell import page_shell
from gui.components.page_title import page_title
from gui.routes import get_path
from tasks.yt_posting import list_unuploaded_videos, upload_generated_video


@ui.page(get_path("Upload Generated Videos"))
def upload_videos_page() -> None:
    page_shell(get_path("Upload Generated Videos"))

    with content():
        back_button(get_path("Channel-wise Workflow"))
        page_title("Upload Generated Videos", "Publish rendered videos that are still marked as not uploaded.")

        list_container = ui.column().classes("w-full gap-3")

        def render_list() -> None:
            list_container.clear()
            videos = list_unuploaded_videos()

            with list_container:
                if not videos:
                    with ui.card().classes("surface w-full p-5"):
                        ui.label("No generated videos are waiting for upload.").classes("muted")
                    return

                for file_name in videos:
                    with ui.card().classes("surface w-full p-4"):
                        with ui.row().classes("w-full items-center justify-between gap-4"):
                            with ui.column().classes("gap-0"):
                                ui.label(file_name).classes("font-semibold")
                                ui.label("Ready to upload").classes("muted text-sm")

                            button = ui.button("Upload", icon="cloud_upload").props("color=primary")

                            async def upload_one(name: str = file_name, upload_button=button) -> None:
                                upload_button.disable()
                                ui.notify(f"Uploading {name}...", type="info")
                                try:
                                    record = await run.io_bound(upload_generated_video, name)
                                except Exception as error:
                                    upload_button.enable()
                                    ui.notify(f"Upload failed: {error}", type="negative")
                                    return

                                ui.notify(
                                    f"Uploaded {name}: {record.get('youtube_url', 'complete')}",
                                    type="positive",
                                )
                                render_list()

                            button.on_click(upload_one)

        async def upload_all() -> None:
            videos = list_unuploaded_videos()
            if not videos:
                ui.notify("No generated videos are waiting for upload.", type="info")
                return

            for file_name in videos:
                try:
                    ui.notify(f"Uploading {file_name}")
                    await run.io_bound(upload_generated_video, file_name)
                    ui.notify(f"Uploaded {file_name}", type="positive")
                except Exception as error:
                    ui.notify(f"Upload failed for {file_name}: {error}", type="negative")
                    break

            render_list()

        with ui.row().classes("w-full justify-end"):
            ui.button("Refresh", icon="refresh", on_click=render_list).props("outline")
            ui.button("Upload All", icon="cloud_upload", on_click=upload_all).props("color=primary")

        render_list()
