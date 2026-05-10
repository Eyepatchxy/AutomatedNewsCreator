from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from tasks.paths import (
    ARTICLES_DIR,
    GENERATED_THUMBNAILS_DIR,
    GENERATED_VIDEOS_DIR,
    UPLOADED_VIDEOS_DIR,
)


SCOPES = ["https://www.googleapis.com/auth/youtube"]
OAUTH_DIR = Path("oAuthSecrets")
TOKEN_FILE = OAUTH_DIR / "youtube_token.json"
VIDEO_DIR = GENERATED_VIDEOS_DIR
THUMBNAIL_DIR = GENERATED_THUMBNAILS_DIR
ARTICLE_DIR = ARTICLES_DIR
UPLOAD_RECORD_DIR = UPLOADED_VIDEOS_DIR

DEFAULT_PRIVACY_STATUS = "public"
NEWS_CATEGORY_ID = "25"
GENERIC_TAGS = [
    "#news",
    "#hindiNews",
    "#breakingNews",
    "#indiaNews",
    "#latestNews",
    "#todayNews",
    "news",
    "hindi news",
    "breaking news",
    "india news",
    "latest news",
    "today news",
]


def load_credentials(token_file: Path = TOKEN_FILE) -> Credentials:
    if not token_file.exists():
        raise FileNotFoundError(
            f"YouTube token not found: {token_file}. "
            "Run oAuthSecrets/authorization.py first."
        )

    creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_file.write_text(creds.to_json(), encoding="utf-8")

    if not creds.valid:
        raise ValueError(
            f"YouTube credentials in {token_file} are invalid. "
            "Run oAuthSecrets/authorization.py again."
        )

    return creds


def get_youtube_client():
    return build("youtube", "v3", credentials=load_credentials())


def load_article(file_name: str) -> dict:
    article_path = ARTICLE_DIR / f"{file_name}.json"
    if not article_path.exists():
        return {}

    with article_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_video(file_name: str) -> Path:
    video_path = VIDEO_DIR / f"{file_name}.mp4"
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    return video_path


def find_thumbnail(file_name: str) -> Path | None:
    for extension in (".jpg", ".jpeg", ".png"):
        thumbnail_path = THUMBNAIL_DIR / f"{file_name}{extension}"
        if thumbnail_path.exists():
            return thumbnail_path
    return None


def clean_title(title: str, fallback: str) -> str:
    title = " ".join((title or fallback).split())
    return title[:100]


def unique_items(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        cleaned = " ".join(str(item).split())
        key = cleaned.lower()
        if cleaned and key not in seen:
            result.append(cleaned)
            seen.add(key)
    return result


def limit_tags(tags: list[str], max_chars: int = 500) -> list[str]:
    limited = []
    total = 0
    for tag in unique_items(tags):
        next_total = total + len(tag) + (1 if limited else 0)
        if next_total > max_chars:
            break
        limited.append(tag)
        total = next_total
    return limited


def build_description(article: dict, tags: list[str]) -> str:
    details = article.get("details") or ""
    source = article.get("source") or ""
    title = article.get("title") or "Latest news update"
    hashtag_line = " ".join(tag for tag in tags if tag.startswith("#"))

    sections = [title, details]
    if source:
        sections.append(f"Source: {source}")
    if hashtag_line:
        sections.append(hashtag_line)

    return "\n\n".join(section.strip() for section in sections if section.strip())[:5000]


def build_upload_metadata(file_name: str, privacy_status: str = DEFAULT_PRIVACY_STATUS) -> dict:
    article = load_article(file_name)
    keywords = article.get("keywords") or []
    article_type = article.get("type") or ""
    title = clean_title(article.get("title"), fallback=f"{file_name} news update")
    tags = limit_tags([*keywords, article_type, *GENERIC_TAGS])
    description = build_description(article, tags)

    return {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": NEWS_CATEGORY_ID,
            "defaultLanguage": "hi",
            "defaultAudioLanguage": "hi",
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,
        },
    }


def upload_video(youtube, video_path: Path, metadata: dict) -> dict:
    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        chunksize=-1,
        resumable=True,
    )
    request = youtube.videos().insert(
        part="snippet,status",
        body=metadata,
        media_body=media,
        notifySubscribers=True,
    )

    response = None
    while response is None:
        _, response = request.next_chunk()
    return response


def set_thumbnail(youtube, video_id: str, thumbnail_path: Path) -> dict:
    media = MediaFileUpload(str(thumbnail_path), resumable=True)
    return youtube.thumbnails().set(
        videoId=video_id,
        media_body=media,
    ).execute()


def save_upload_record(file_name: str, record: dict) -> Path:
    UPLOAD_RECORD_DIR.mkdir(exist_ok=True)
    record_path = UPLOAD_RECORD_DIR / f"{file_name}.json"
    with record_path.open("w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return record_path


def publish_to_youtube(
    file_name: str,
    privacy_status: str = DEFAULT_PRIVACY_STATUS,
    dry_run: bool = False,
) -> dict:
    video_path = find_video(file_name)
    thumbnail_path = find_thumbnail(file_name)
    metadata = build_upload_metadata(file_name, privacy_status)

    record = {
        "file_name": file_name,
        "video_path": str(video_path),
        "thumbnail_path": str(thumbnail_path) if thumbnail_path else None,
        "metadata": metadata,
        "dry_run": dry_run,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }

    if dry_run:
        record["status"] = "dry_run"
        record["thumbnail_status"] = "found" if thumbnail_path else "not_found"
        save_upload_record(file_name, record)
        return record

    youtube = get_youtube_client()
    upload_response = upload_video(youtube, video_path, metadata)
    video_id = upload_response["id"]

    record.update(
        {
            "status": "uploaded",
            "video_id": video_id,
            "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
            "upload_response": upload_response,
            "thumbnail_status": "not_found",
        }
    )

    if thumbnail_path:
        try:
            record["thumbnail_response"] = set_thumbnail(youtube, video_id, thumbnail_path)
            record["thumbnail_status"] = "uploaded"
        except HttpError as exc:
            record["thumbnail_status"] = "failed"
            record["thumbnail_error"] = str(exc)

    save_upload_record(file_name, record)
    return record


def main():
    parser = argparse.ArgumentParser(description="Upload a generated video to YouTube.")
    parser.add_argument(
        "file_name",
        help="Base file name, for example 2026-05-10_18-24-30_ai-protein-folding-breakthrough",
    )
    parser.add_argument(
        "--privacy",
        choices=["public", "unlisted", "private"],
        default=DEFAULT_PRIVACY_STATUS,
        help="YouTube privacy status. Defaults to public.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build metadata and save a record without uploading.",
    )
    args = parser.parse_args()

    record = publish_to_youtube(
        args.file_name,
        privacy_status=args.privacy,
        dry_run=args.dry_run,
    )

    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
