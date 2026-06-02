import json
import os
import sys
from pathlib import Path

from nicegui import run, ui

from gui.state.models import VideoType
from gui.components.progress_pipeline import ProgressPipeline
from gui.utils.constants import VIDEO_STAGES
from paths import FONT_FILE


FILE_NAME = "2026-06-02_18-37-01_cbse-website-hack"
HEADLINE = ""
FONT_PATH = FONT_FILE


def render_video(file_name: str, pipeline: ProgressPipeline) -> str:
    if Path(FONT_PATH).exists():
        os.environ.setdefault("VIDEO_TEXT_FONT", str(FONT_PATH))

    from tasks.video_generator import generate_video

    chunks_file = Path("Generated/Chunks") / f"{file_name}.json"
    audio_file = Path("Generated/Audios") / f"{file_name}.wav"

    chunks = json.loads(chunks_file.read_text(encoding="utf-8"))
    return generate_video(
        file_name,
        chunks,
        audio_file,
        pipeline=pipeline,
        headline_text=HEADLINE,
        video_type=VideoType.SHORT
    )


@ui.page("/")
def test_pipeline_page() -> None:
    file_name = sys.argv[1] if len(sys.argv) > 1 else FILE_NAME

    ui.label("Video Render Pipeline Test").classes("text-2xl font-semibold")
    ui.label(file_name).classes("text-sm text-slate-500")

    pipeline = ProgressPipeline(stages=VIDEO_STAGES)
    result_label = ui.label("").classes("text-sm text-slate-500")

    async def start_render() -> None:
        for stage_no in range(1, 8):
            pipeline.start_stage(stage_no)
            pipeline.complete_stage(stage_no)

        pipeline.log.push("Starting video render test")

        try:
            output_file = await run.io_bound(render_video, file_name, pipeline)
        except Exception as error:
            pipeline.fail_stage(pipeline.current_stage, str(error))
            result_label.text = "Render failed. Check the log."
            return

        pipeline.log.push("Uploading skipped for render test")
        pipeline.complete_stage(9)
        pipeline.complete_pipeline()
        result_label.text = f"Video: {output_file}"

    ui.timer(0.1, start_render, once=True)


if __name__ == "__main__":
    ui.run(title="Pipeline Render Test", reload=False)
