from dotenv import load_dotenv
load_dotenv()

import argparse
import sys
import math
from moviepy import AudioFileClip

from tasks.audio_generator import generate_audio
from tasks.chunk_generator import generate_chunks
from tasks.filename_utils import build_file_name
from tasks.thumbnail_generator import generate_thumbnail
from tasks.timeline_parser import build_timeline
from tasks.backimage_generator import generate_backimages
from tasks.script_generator import generate_script
from tasks.video_generator import generate_video
from tasks.yt_posting import DEFAULT_PRIVACY_STATUS, publish_to_youtube
from tasks.ExtractionTools.news_verifier import verify_news


sys.stdout.reconfigure(encoding="utf-8")


def build_headline_text(article):
    article_type = article.get("type")
    if article_type:
        return f"{article_type.strip().lower().capitalize()} News"
    return "Breaking News"


def get_verified_article():
    verified_data = verify_news()
    if not verified_data:
        return None

    for article in verified_data.get("articles", []):
        if article.get("isTrue"):
            return article

    return None


def run_pipeline(upload=False, privacy=DEFAULT_PRIVACY_STATUS, dry_run_upload=False):
    article = get_verified_article()
    if not article:
        raise RuntimeError("No verified article found in processed news.")

    file_name = build_file_name(article.get("title", "news-update"))

    article_details = article.get("details", "")
    script = generate_script(file_name, article_details)
    chunks = generate_chunks(file_name, script)
    thumbnail_file = generate_thumbnail(file_name)
    audio_file = generate_audio(file_name, script)

    audio = AudioFileClip(str(audio_file))
    duration = math.ceil(audio.duration)

    timeline = build_timeline(file_name, chunks, duration)
    backimages = generate_backimages(file_name, timeline, duration)
    headline=build_headline_text(article)

    video_file = generate_video(
        file_name,
        chunks,
        audio_file,
        headline,
    )

    print("Pipeline complete.")
    print(f"Filename: {file_name}")
    print(f"Audio: {audio_file}")
    print(f"Video: {video_file}")
    print(f"Thumbnail: {thumbnail_file}")
    if upload or dry_run_upload:
        upload_record = publish_to_youtube(
            file_name,
            privacy_status=privacy,
            dry_run=dry_run_upload,
        )
        if dry_run_upload:
            print(f"YouTube dry-run record saved")
        else:
            print(f"YouTube video uploaded: {upload_record['youtube_url']}")

    return video_file


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Hindi news video from article to audio to final render."
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload the generated video to YouTube after rendering.",
    )
    parser.add_argument(
        "--privacy",
        choices=["public", "unlisted", "private"],
        default=DEFAULT_PRIVACY_STATUS,
        help=f"YouTube privacy status when --upload is used. Defaults to {DEFAULT_PRIVACY_STATUS}.",
    )
    parser.add_argument(
        "--dry-run-upload",
        action="store_true",
        help="Build the YouTube upload record without uploading. Implies --upload.",
    )
    args = parser.parse_args()

    run_pipeline(
        upload=args.upload,
        privacy=args.privacy,
        dry_run_upload=args.dry_run_upload,
    )


if __name__ == "__main__":
    main()
