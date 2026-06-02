import json

from dotenv import load_dotenv
from paths import PROJECT_ROOT
load_dotenv(PROJECT_ROOT / ".env")

import sys
import math
from moviepy import AudioFileClip
from paths import GENERATED_ARTICLES_DIR
from tasks.news_verifier import verify_news
from tasks.audio_generator import generate_audio
from tasks.chunk_generator import generate_chunks
from tasks.filename_utils import build_file_name
from tasks.thumbnail_generator import generate_thumbnail
from tasks.timeline_parser import build_timeline
from tasks.backimage_generator import generate_backimages
from tasks.script_generator import generate_script
from tasks.video_generator import generate_video
from tasks.yt_posting import (
    DEFAULT_PRIVACY_STATUS,
    publish_to_youtube,
    save_generated_video_record,
)
from tasks.ExtractionTools.channelwise_news_extractor import (
    create_youtube_client,
    get_recent_videos,
)
from tasks.ExtractionTools.deduplicator import semantic_deduplicate
from gui.components.progress_pipeline import ProgressPipeline
from gui.state.models import VideoDuration, VideoType

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")

GENEERATE_THUMBNAIL_FOR_SHORTS = False


def video_pipeline(
    title,
    description,
    pipeline:ProgressPipeline,
    target_time=90,
    video_type=VideoType.FULL,
    upload=True,
    privacy=DEFAULT_PRIVACY_STATUS,
    dry_run_upload=False
):

    file_name = verify_news(pipeline=pipeline, title=title, description=description)
    if not file_name:
        raise RuntimeError("[INFO] News verification did not produce an article.")

    with open(f"{GENERATED_ARTICLES_DIR}/{file_name}.json", "r", encoding="utf-8") as f:
        article = json.load(f)    
    
    if not article:
        raise RuntimeError("[INFO] No generated article found.")

    article_details = article.get("details", "")
    if isinstance(target_time, VideoDuration):
        target_time = target_time.value

    video_type = VideoType(video_type or VideoType.FULL)

    script = generate_script(
        file_name,
        article_details,
        pipeline=pipeline,
        target_time=target_time,
        video_type=video_type,
    )
    audio_file = generate_audio(file_name, script, pipeline=pipeline)
    audio = AudioFileClip(str(audio_file))
    duration = math.ceil(audio.duration)
    audio.close()

    chunks = generate_chunks(file_name, script, pipeline=pipeline, duration=duration)
    timeline = build_timeline(file_name, chunks, duration, pipeline=pipeline)
    if video_type == VideoType.SHORT and not GENEERATE_THUMBNAIL_FOR_SHORTS:
        thumbnail_file = None
        pipeline.start_stage(6)
        pipeline.log.push("Thumbnail generation skipped for short video")
        pipeline.complete_stage(6)
    else:
        thumbnail_file = generate_thumbnail(
            file_name,
            pipeline=pipeline,
            video_type=video_type,
        )
    backimages = generate_backimages(
        file_name,
        timeline,
        duration,
        pipeline=pipeline,
        video_type=video_type,
    )
    headline=build_headline_text(article.get("type"))

    video_file = generate_video(
        file_name,
        chunks,
        audio_file,
        pipeline=pipeline,
        headline_text=headline,
        video_type=video_type,
    )
    save_generated_video_record(
        file_name,
        privacy_status=privacy,
        video_type=video_type,
    )

    print("Pipeline complete.")
    print(f"Filename: {file_name}")
    print(f"Audio: {audio_file}")
    print(f"Video: {video_file}")
    print(f"Thumbnail: {thumbnail_file if thumbnail_file else 'skipped'}")
    if upload:
        upload_record = publish_to_youtube(
            file_name,
            pipeline=pipeline,
            privacy_status=privacy,
            dry_run=dry_run_upload,
            video_type=video_type,
        )
        if dry_run_upload:
            print(f"YouTube dry-run record saved")
        else:
            print(f"YouTube video uploaded: {upload_record['youtube_url']}")
    else:
        pipeline.log.push("Uploading skipped")
        pipeline.complete_stage(9)

    return video_file


def channelwise_extraction_pipeline(
    channel_priorities=None,
    num_videos=5
):
    
    youtube_client = create_youtube_client()
    get_recent_videos(
        youtube_client,
        selected_channel_priorities=channel_priorities,
        max_results_per_channel=num_videos,
    )
    return semantic_deduplicate()


def build_headline_text(type):
    headline_map = {
        "politics": "राजनीति न्यूज़",
        "tech": "टेक न्यूज़",
        "technology": "टेक न्यूज़",
        "business": "बिज़नेस न्यूज़",
        "global": "ग्लोबल न्यूज़",
        "world": "विश्व न्यूज़",
        "sports": "स्पोर्ट्स न्यूज़",
        "entertainment": "मनोरंजन न्यूज़",
        "general": "ताज़ा न्यूज़",
    }
    if type:
        return headline_map.get(type.strip().lower(), "ताज़ा न्यूज़")
    return "ताज़ा न्यूज़"
