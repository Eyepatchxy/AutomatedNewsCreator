from nicegui import run, ui
from gui.components.page_title import page_title
from gui.components.content import content
from gui.components.page_shell import page_shell
from gui.components.buttons import back_button
from gui.components.progress_pipeline import ProgressPipeline
from gui.utils.constants import VIDEO_STAGES
from gui.routes import get_path
from gui.services.pipeline_service import run_video_generation_job
from gui.state.app_state import STATE

@ui.page(get_path("Video Generation Progress"))
def video_progress_page() -> None:
    page_shell()
    with content():
        back_button(get_path("Video Configuration"))
        page_title("Video Generation Progress", "Generating script, audio, visuals, and final video.")
        pipeline = ProgressPipeline(
            VIDEO_STAGES,
            "Video generation",
            "Running",
            auto_tick=True,
            tick_seconds=6.0,
        )
        result_label = ui.label("").classes("muted")

        async def start_job() -> None:
            job = STATE.get("video_job")
            if not job:
                pipeline.fail("No video job was queued.")
                result_label.text = "Return to video configuration and start generation again."
                return

            pipeline.log.push("Video generation: running real video_pipeline")
            try:
                result = await run.io_bound(run_video_generation_job)
            except Exception as error:
                STATE["video_job"] = {**job, "status": "failed", "error": str(error)}
                pipeline.fail(str(error))
                result_label.text = "Video generation failed. Check the log and generated files."
                return

            pipeline.finish_success("Video file created")
            result_label.text = f"Video: {result}"

        ui.timer(0.1, start_job, once=True)
