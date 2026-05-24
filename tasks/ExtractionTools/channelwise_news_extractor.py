import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from paths import TOKEN_FILE, RAW_NEWS_POOL_FILE, CHANNELS_FILE
from tasks.ExtractionTools.deduplicator import normalize_text

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

MAX_RESULTS_PER_CHANNEL = 5

def create_youtube_client():
    """
    Creates authenticated YouTube API client
    using OAuth token.json
    """

    creds = Credentials.from_authorized_user_file(
        TOKEN_FILE,
    )

    youtube = build(
        "youtube",
        "v3",
        credentials=creds
    )

    return youtube


def get_channel_id_from_handle(
    youtube,
    handle
):
    """
    Converts @handle to channel ID
    """

    handle = handle.replace("@", "")

    response = youtube.channels().list(
        part="id,snippet",
        forHandle=handle
    ).execute()

    items = response.get("items", [])

    if not items:
        print(f"Channel not found: @{handle}")
        return None

    return items[0]["id"]


def get_recent_videos(
    youtube,
    days=7,
    output_file=RAW_NEWS_POOL_FILE,
    selected_channel_priorities=None,
    max_results_per_channel=MAX_RESULTS_PER_CHANNEL,
):
    """
    Fetch recent videos from channels
    and save to JSON
    """

    channels = json.load(open(CHANNELS_FILE, encoding="utf-8"))["channels"]

    published_after = (
        datetime.now(timezone.utc)
        - timedelta(days=days)
    ).isoformat()

    selected_priorities = set(selected_channel_priorities or [])
    selected_channels = [
        channel
        for channel in channels
        if not selected_priorities or channel["priority"] in selected_priorities
    ]

    all_videos = []

    for channel in selected_channels:

        print(f"Fetching: {channel['name']}")

        channel_id = channel.get("id")

        if not channel_id:
            print(f"Channel ID missing: {channel['name']}")
            continue

        response = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            order="date",
            publishedAfter=published_after,
            maxResults=max_results_per_channel
        ).execute()

        for item in response.get("items", []):

            video = {
                "video_id": normalize_text(item["id"]["videoId"]),

                "title": normalize_text(item["snippet"]["title"]),

                "description": normalize_text(item["snippet"]["description"]),

                "published_at": item["snippet"]["publishedAt"],

                "channel": normalize_text(item["snippet"]["channelTitle"]),

                "channel_id": channel_id,

                "priority": channel["priority"],

                "url": (
                    f"https://youtube.com/watch?"
                    f"v={item['id']['videoId']}"
                )
            }

            all_videos.append(video)

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Save JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            all_videos,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Saved {len(all_videos)} videos "
        f"to {output_file}"
    )

    return all_videos
