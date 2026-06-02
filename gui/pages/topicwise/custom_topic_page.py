from nicegui import run, ui
from gui.components.page_title import page_title
from gui.components.content import content
from gui.components.page_shell import page_shell
from gui.components.cards import stat_card
from gui.components.buttons import back_button
from gui.state.models import NewsItem
from gui.state.app_state import STATE
from gui.routes import get_path
from gui.services.pipeline_service import prepare_video_job



@ui.page(get_path("Topic-wise Workflow"))
def custom_topic_page() -> None:
    page_shell(get_path("Topic-wise Workflow"))

    with content():
        back_button(get_path("Home"))
        page_title("Custom Topic", "Describe the story you want to turn into a video.")
        topic = ui.input("Topic").props("outlined").classes("w-full")
        description = ui.textarea("Small Description").props("outlined").classes("w-full")
        category = ui.select(
            ["Politics", "Business", "Technology", "Sports", "Entertainment", "World", "General"],
            value="General",
            label="Category",
        ).props("outlined").classes("w-full")
        analysis = ui.column().classes("w-full")
        status_label = ui.label("").classes("muted")

        async def analyze_topic() -> None:
            clean_topic = (topic.value or "").strip()
            clean_description = (description.value or "").strip()
            if not clean_topic and not clean_description:
                ui.notify("Enter a topic or use Quick Generate.", type="warning")
                return

            clean_category = category.value or "General"
            status_label.text = "Analyzing topic..."
            analyze_button.disable()

            try:
                from tasks.ExtractionTools.topicwise_news_extractor import topicwise_news_extractor

                result = await run.io_bound(
                    topicwise_news_extractor,
                    clean_topic,
                    clean_description,
                )
            except Exception as error:
                status_label.text = ""
                analyze_button.enable()
                ui.notify(f"Topic analysis failed: {error}", type="negative")
                return

            analyze_button.enable()
            status_label.text = ""

            articles = (result or {}).get("articles", []) if isinstance(result, dict) else []
            verified_article = next(
                (article for article in articles if article.get("isTrue")),
                None,
            )

            if not verified_article:
                ui.notify("No verified article was generated.", type="warning")
                return

            STATE["custom_topic"] = {
                "topic": verified_article.get("title", clean_topic),
                "description": verified_article.get("details", clean_description),
                "category": verified_article.get("type", clean_category),
            }
            STATE["selected_news"] = NewsItem(
                headline=verified_article.get("title", clean_topic),
                category=verified_article.get("type", clean_category),
                confidence=0.87,
                source_count=1,
                summary=verified_article.get("details", clean_description),
            )
            analysis.clear()
            with analysis:
                with ui.card().classes("surface w-full p-6 gap-4"):
                    ui.label("Topic Analysis").classes("text-xl font-semibold")
                    with ui.row().classes("w-full gap-4"):
                        stat_card("Detected Topic", verified_article.get("title", clean_topic), "radar")
                        stat_card("Detected Category", verified_article.get("type", clean_category), "category")
                        stat_card("Verification", "Passed", "verified")
                    ui.label("Verified Summary").classes("font-semibold")
                    ui.label(verified_article.get("details", "")).classes("muted leading-6")
                    ui.label("Do you want to generate a video on this topic?").classes(
                        "text-lg font-semibold"
                    )
                    with ui.row().classes("w-full justify-between"):
                        ui.button("Back", icon="arrow_back", on_click=lambda: ui.navigate.to(get_path("Home"))).props(
                            "outline color=grey-8"
                        )
                        ui.button(
                            "Continue To Video Configuration",
                            icon="arrow_forward",
                            on_click=lambda: ui.navigate.to(get_path("Video Configuration")),
                        ).props("color=primary")

        def quick_generate() -> None:
            prepare_video_job("", "", upload=STATE.get("upload_job", True))
            ui.navigate.to(get_path("Video Generation Progress"))

        with ui.row().classes("w-full justify-end"):
            ui.button("Quick Generate", icon="bolt", on_click=quick_generate).props(
                "outline color=primary"
            )
            analyze_button = ui.button("Analyze Topic", icon="auto_awesome", on_click=analyze_topic).props(
                "color=primary"
            )

            def update_analyze_button() -> None:
                if (topic.value or "").strip() or (description.value or "").strip():
                    analyze_button.enable()
                else:
                    analyze_button.disable()

            topic.on_value_change(lambda _: update_analyze_button())
            description.on_value_change(lambda _: update_analyze_button())
            update_analyze_button()
        status_label
        analysis
