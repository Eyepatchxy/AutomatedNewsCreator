from nicegui import ui
from gui.components.page_title import page_title
from gui.components.content import content
from gui.components.page_shell import page_shell
from gui.components.buttons import back_button
from gui.state.app_state import STATE
from gui.services.news_service import load_processed_news

@ui.page("/yt/processed-news")
def processed_news_page() -> None:
    page_shell("yt")
    news_items = load_processed_news()
    selected_index = {"value": 0}
    STATE["selected_news"] = news_items[0]

    with content():
        back_button("/yt")
        page_title("Processed News", "Select one story to use as the basis for a generated video.")
        cards = ui.column().classes("w-full gap-3")

        def render_cards() -> None:
            cards.clear()
            with cards:
                for index, item in enumerate(news_items):
                    active = index == selected_index["value"]
                    with ui.card().classes(
                        f"surface w-full cursor-pointer p-5 border-2 {'border-primary' if active else 'border-transparent'}"
                    ).on("click", lambda _, i=index: select_item(i)):
                        with ui.row().classes("w-full items-start justify-between gap-4"):
                            with ui.column().classes("gap-2 flex-1"):
                                ui.label(item.headline).classes("text-lg font-semibold")
                                if item.summary:
                                    ui.label(item.summary).classes("muted text-sm")
                            with ui.row().classes("gap-2"):
                                ui.badge(item.category).props("outline color=primary")
                                ui.badge(f"{item.confidence:.0%} confidence").props("outline color=green")
                                ui.badge(f"{item.source_count} sources").props("outline color=grey")

        def select_item(index: int) -> None:
            selected_index["value"] = index
            STATE["selected_news"] = news_items[index]
            render_cards()

        render_cards()
        with ui.row().classes("w-full justify-end"):
            ui.button(
                "Continue To Video Configuration",
                icon="arrow_forward",
                on_click=lambda: ui.navigate.to("/video/config"),
            ).props("color=primary")