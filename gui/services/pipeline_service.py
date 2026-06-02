from gui.services.channel_service import selected_channel_priorities
from gui.services.news_service import remove_processed_news
from gui.state.app_state import STATE
from gui.state.models import NewsItem
from gui.components.progress_pipeline import ProgressPipeline
from gui.utils.CancelException import PipelineCancelled

def prepare_extraction_job() -> None:
    STATE["extraction_job"] = {
        "status": "queued",
        "channel_priorities": selected_channel_priorities(),
        "num_videos": 5,
        "result": None,
        "error": None,
    }


def prepare_video_job_from_selection(upload: bool | None = None) -> None:
    selected_news = STATE.get("selected_news")
    if isinstance(selected_news, NewsItem):
        title = selected_news.headline
        description = selected_news.summary
        remove_after_generation = True
    else:
        title = ""
        description = ""
        remove_after_generation = False

    prepare_video_job(
        title,
        description,
        upload=STATE.get("upload_job", True) if upload is None else upload,
        remove_after_generation=remove_after_generation,
    )


def prepare_video_job(
    title: str,
    description: str,
    upload: bool = True,
    remove_after_generation: bool = False,
) -> None:
    STATE["video_job"] = {
        "status": "queued",
        "title": title,
        "description": description,
        "upload": upload,
        "remove_after_generation": remove_after_generation,
        "result": None,
        "error": None,
    }


def run_channelwise_extraction_job() -> list[dict]:
    from main import channelwise_extraction_pipeline

    job = STATE.get("extraction_job") or {}
    result = channelwise_extraction_pipeline(
        channel_priorities=job.get("channel_priorities"),
        num_videos=job.get("num_videos", 5),
    )
    STATE["extraction_job"] = {
        **job,
        "status": "completed",
        "result": result,
        "error": None,
    }
    return result


def run_video_generation_job(pipeline:ProgressPipeline):
    from main import video_pipeline

    job = STATE.get("video_job") or {}
    try:
        result = video_pipeline(
            title=job.get("title", ""),
            description=job.get("description", ""),
            pipeline=pipeline,
            target_time=STATE.get("target_time", 90),
            upload=STATE.get("upload_job", True),
        )
    except PipelineCancelled:
        pipeline.log.push(
            "Generation cancelled by user"
        )
        STATE["video_job"] = {**job, "status": "cancelled", "error": "Generation cancelled by user"}
        raise
    except Exception as e:
        pipeline.fail_stage(pipeline.current_stage, str(e))
        STATE["video_job"] = {**job, "status": "failed", "error": str(e)}
        raise

    removed_processed_news = False
    if job.get("remove_after_generation"):
        removed_processed_news = remove_processed_news(
            job.get("title", ""),
            job.get("description", ""),
        )

    STATE["video_job"] = {
        **job,
        "status": "completed",
        "result": str(result),
        "removed_processed_news": removed_processed_news,
        "error": None,
    }
    return result
