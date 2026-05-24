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
        back_button(get_path("Extraction Confirmation"))
        page_title("Extraction Progress", "Fetching videos and deduplicating channel news.")
        pipeline = ProgressPipeline(
            EXTRACTION_STAGES,
            "Extraction",
            "Running",
            auto_tick=True,
            tick_seconds=5.0,
        )
        result_label = ui.label("").classes("muted")

        async def start_job() -> None:
            job = STATE.get("extraction_job")
            if not job:
                pipeline.fail("No extraction job was queued.")
                result_label.text = "Return to channel selection and start extraction again."
                return

            pipeline.log.push("Extraction: running real channelwise_extraction_pipeline")
            try:
                result = await run.io_bound(run_channelwise_extraction_job)
            except Exception as error:
                STATE["extraction_job"] = {**job, "status": "failed", "error": str(error)}
                pipeline.fail(str(error))
                result_label.text = "Extraction failed. Check the log and credentials."
                return

            pipeline.finish_success(f"Saved {len(result)} processed stories")
            result_label.text = f"Processed stories: {len(result)}"

        ui.timer(0.1, start_job, once=True)
