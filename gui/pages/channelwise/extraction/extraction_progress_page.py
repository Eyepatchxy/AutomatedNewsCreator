from nicegui import run, ui
from gui.components.page_title import page_title
from gui.components.content import content
from gui.components.page_shell import page_shell
from gui.components.buttons import back_button
from gui.components.progress_pipeline import ProgressPipeline
from gui.utils.constants import EXTRACTION_STAGES
from gui.routes import get_path
from gui.services.pipeline_service import run_channelwise_extraction_job
from gui.state.app_state import STATE

@ui.page(get_path("Extraction Progress"))
def extraction_progress_page() -> None:
    page_shell(get_path("Extraction Progress"))
    with content():
        with ui.row().classes("w-full justify gap-8"):
            with ui.element("div").classes("flex-1"):
                back_button(get_path("Extraction Confirmation"))

            with ui.element("div").classes("flex justify-center"):
                page_title(
                    "Extraction Progress",
                    "Fetching videos and deduplicating channel news.",
                )

            with ui.element("div").classes("flex-1 flex justify-end"):
                navigate_button = ui.button(
                    "Continue",
                    icon="arrow_forward",
                    on_click=lambda: ui.navigate.to(get_path("Processed News")),
                ).props("color=primary")
                navigate_button.visible = False
            
        pipeline = ProgressPipeline(
            EXTRACTION_STAGES,
        )
        result_label = ui.label("").classes("muted")

        async def start_job() -> None:
            job = STATE.get("extraction_job")
            if not job:
                pipeline.fail_stage(None, "No extraction job was queued.")
                result_label.text = "Return to channel selection and start extraction again."
                return

            pipeline.log.push("Extraction: running real channelwise_extraction_pipeline")
            try:
                result = await run.io_bound(run_channelwise_extraction_job)
            except Exception as error:
                STATE["extraction_job"] = {**job, "status": "failed", "error": str(error)}
                pipeline.fail_stage(pipeline.current_stage, str(error))
                result_label.text = "Extraction failed. Check the log and credentials."
                return

            pipeline.finish_success(f"Saved {len(result)} processed stories")
            result_label.text = f"Processed stories: {len(result)}"
            navigate_button.visible = True

        ui.timer(0.1, start_job, once=True)
