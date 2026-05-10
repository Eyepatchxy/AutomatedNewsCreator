from dotenv import load_dotenv
load_dotenv()

import argparse
import json
import os

from tasks.video_generator import generate_video
from tasks.yt_posting import DEFAULT_PRIVACY_STATUS, publish_to_youtube
from tasks.paths import ARTICLES_DIR, GENERATED_AUDIOS_DIR, GENERATED_CHUNKS_DIR


def main():
    parser = argparse.ArgumentParser(
        description="Generate video after audio is ready, optionally upload it to YouTube."
    )
    parser.add_argument(
        "file_name",
        help="Base file name, for example 2026-05-10_18-24-30_ai-protein-folding-breakthrough",
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

    file_name = args.file_name
    chunks_file = GENERATED_CHUNKS_DIR / f"{file_name}.json"
    audio_file = GENERATED_AUDIOS_DIR / f"{file_name}.wav"

    if not os.path.exists(chunks_file):
        raise FileNotFoundError(f"Chunks file not found: {chunks_file}")

    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    headline_text = "Breaking News"
    article_file = ARTICLES_DIR / f"{file_name}.json"
    if os.path.exists(article_file):
        with open(article_file, "r", encoding="utf-8") as f:
            article = json.load(f)
        article_type = article.get("type")
        if article_type:
            article_type = article_type.strip().lower().capitalize()
            headline_text = f"{article_type} News"

    video_file = generate_video(file_name, chunks, audio_file, headline_text)
    print(f"Video generated: {video_file}")

    if args.upload or args.dry_run_upload:
        upload_record = publish_to_youtube(
            file_name,
            privacy_status=args.privacy,
            dry_run=args.dry_run_upload,
        )
        if args.dry_run_upload:
            print(f"YouTube dry-run record saved for: {file_name}")
        else:
            print(f"YouTube video uploaded: {upload_record['youtube_url']}")


if __name__ == "__main__":
    main()
