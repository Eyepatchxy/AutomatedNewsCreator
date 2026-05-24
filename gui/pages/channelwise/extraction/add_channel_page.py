from nicegui import ui

from gui.components.buttons import back_button
from gui.components.content import content
from gui.components.page_shell import page_shell
from gui.components.page_title import page_title
from gui.routes import get_path
from gui.services.channel_service import add_channel, next_priority_slot, priority_choices
from gui.state.app_state import STATE


@ui.page(get_path("Add Channel"))
def add_channel_page() -> None:
    page_shell(get_path("Add Channel"))

    with content():
        back_button(get_path("Channel Selection"))
        page_title("Add Channel", "Add a YouTube channel by handle or username.")

        with ui.card().classes("surface w-full p-5 gap-4"):
            handle_input = ui.input("YouTube handle or username").props(
                "outlined clearable"
            ).classes("w-full")
            priority_select = ui.select(
                priority_choices(),
                label="Priority",
                value=next_priority_slot(),
            ).props("outlined").classes("w-full")

            with ui.row().classes("w-full justify-end gap-3"):
                ui.button(
                    "Cancel",
                    icon="close",
                    on_click=lambda: ui.navigate.to(get_path("Channel Selection")),
                ).props("outline color=grey-8")

                def submit_channel() -> None:
                    identifier = (handle_input.value or "").strip()
                    if not identifier:
                        ui.notify("Enter a YouTube handle or username.", type="warning")
                        return

                    try:
                        channel = add_channel(identifier, int(priority_select.value))
                    except ValueError as error:
                        STATE["channel_flash"] = {
                            "message": str(error),
                            "type": "negative",
                        }
                        ui.navigate.to(get_path("Channel Selection"))
                        return
                    except Exception as error:
                        STATE["channel_flash"] = {
                            "message": f"Could not add channel: {error}",
                            "type": "negative",
                        }
                        ui.navigate.to(get_path("Channel Selection"))
                        return

                    selected_channels = set(STATE["selected_channels"])
                    selected_channels.add(channel.channel_id)
                    STATE["selected_channels"] = list(selected_channels)
                    STATE["channel_flash"] = {
                        "message": f"Added {channel.name}.",
                        "type": "positive",
                    }
                    ui.navigate.to(get_path("Channel Selection"))

                ui.button("Add Channel", icon="add", on_click=submit_channel).props(
                    "color=primary"
                )
