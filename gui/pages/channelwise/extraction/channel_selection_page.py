from nicegui import ui
from gui.components.page_shell import page_shell
from gui.components.page_title import page_title
from gui.components.buttons import back_button
from gui.components.content import content
from gui.state.app_state import STATE
from gui.services.channel_service import load_channels
from gui.routes import get_path


@ui.page(get_path("Channel Selection"))
def channel_selection_page() -> None:
    page_shell(get_path("Channel Selection"))
    channels = load_channels()
    visible_channels = channels.copy()
    search_term = ""

    with content():
        back_button(get_path("Channel-wise Workflow"))
        with ui.row().classes("w-full items-center justify-between gap-4"):
            page_title("Select Channels", "Choose the channels to include in the next extraction run.")
            ui.button(
                "Add Channel",
                icon="add",
                on_click=lambda: ui.navigate.to(get_path("Add Channel")),
            ).props("color=primary")

        flash = STATE.pop("channel_flash", None)
        if flash:
            ui.timer(
                0.1,
                lambda: ui.notify(flash["message"], type=flash["type"]),
                once=True,
            )

        selected = set(STATE["selected_channels"])
        list_container = ui.column().classes("w-full gap-3")

        def apply_filter() -> None:
            query = search_term.strip().lower()
            visible_channels.clear()
            visible_channels.extend(
                channel
                for channel in channels
                if query in channel.name.lower() or query in channel.handle.lower()
            )

        def render_list() -> None:
            list_container.clear()
            with list_container:
                if not visible_channels:
                    ui.label("No channels match your search.").classes("muted")
                    return
                for channel in visible_channels:
                    with ui.card().classes("surface w-full p-4"):
                        with ui.row().classes("w-full items-center justify-between gap-4"):
                            with ui.row().classes("items-center gap-3"):
                                checkbox = ui.checkbox(value=channel.channel_id in selected)
                                with ui.column().classes("gap-0"):
                                    ui.label(channel.name).classes("font-semibold")
                                    ui.label(f"{channel.handle} - Priority {channel.priority}").classes(
                                        "muted text-sm"
                                    )

                            def toggle(value: bool, channel_id: str = channel.channel_id) -> None:
                                if value:
                                    selected.add(channel_id)
                                else:
                                    selected.discard(channel_id)
                                STATE["selected_channels"] = list(selected)

                            checkbox.on_value_change(lambda event, fn=toggle: fn(event.value))

        def filter_channels(term: str) -> None:
            nonlocal search_term
            query = (term or "").strip().lower()
            search_term = query
            apply_filter()
            render_list()

        def set_all(checked: bool) -> None:
            if checked:
                selected.update(channel.channel_id for channel in channels)
            else:
                selected.clear()
            STATE["selected_channels"] = list(selected)
            render_list()

        with ui.card().classes("surface w-full p-5 gap-4"):
            with ui.row().classes("w-full items-center gap-3"):
                ui.input("Search channels", on_change=lambda event: filter_channels(event.value)).props(
                    "outlined clearable"
                ).classes("flex-1")
                ui.button("Select All", icon="done_all", on_click=lambda: set_all(True)).props(
                    "outline"
                )
                ui.button("Deselect All", icon="remove_done", on_click=lambda: set_all(False)).props(
                    "outline color=grey-8"
                )
            render_list()

        with ui.row().classes("w-full justify-end"):
            ui.button(
                "Continue",
                icon="arrow_forward",
                on_click=lambda: ui.navigate.to(get_path("Extraction Confirmation")),
            ).props("color=primary")
