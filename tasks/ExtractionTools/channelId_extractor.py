import json

from paths import TOKEN_FILE, CHANNELS_FILE


def create_youtube_client():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    return build("youtube", "v3", credentials=creds)


def _clean_identifier(identifier: str) -> str:
    value = (identifier or "").strip()

    if "youtube.com/" in value:
        value = value.rstrip("/").split("youtube.com/", 1)[1]
        value = value.split("?", 1)[0].split("&", 1)[0]
        if value.startswith("@"):
            return value
        if value.startswith("c/") or value.startswith("user/"):
            return value.split("/", 1)[1]

    return value


def get_channel_metadata(identifier: str) -> dict | None:
    youtube = create_youtube_client()
    cleaned = _clean_identifier(identifier)
    lookup_value = cleaned.lstrip("@")
    handle = handle = f"@{lookup_value}"

    if not handle:
        return None
    
    try:
        response = youtube.channels().list(
            part="id,snippet",
            forHandle=handle,
        ).execute()
    except Exception as error:
        raise RuntimeError(
        f"Failed to fetch YouTube channel '{handle}'"
    ) from error

    items = response.get("items", [])
    if not items:
        raise RuntimeError(
        f"Failed to fetch YouTube channel '{handle}'"
    ) from error

    item = items[0]

    channel_id = item.get("id")
    channel_name = item.get("snippet", {}).get("title")

    if not channel_id or not channel_name:
        print(f"Incomplete channel data for: {identifier}")
        return None

    return {
        "id": channel_id,
        "name": channel_name,
        "handle": handle,
    }


def get_channel_id(identifier: str) -> str | None:
    metadata = get_channel_metadata(identifier)
    return metadata["id"] if metadata else None


def update_channel_ids(channels_file=CHANNELS_FILE):

    # Load channels
    with open(channels_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    channels = data.get("channels", data if isinstance(data, list) else [])

    # Update IDs
    for channel in channels:

        handle = channel.get("handle")

        if not handle:
            continue

        print(f"Fetching ID for {handle}")

        metadata = get_channel_metadata(handle)

        if metadata:
            channel["id"] = metadata["id"]
            channel["name"] = channel.get("name") or metadata["name"]
            print(f"Updated: {handle}")
        else:
            print(f"Failed: {handle}")

    # Save updated JSON
    with open(channels_file, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

    print("channels.json updated successfully.")


if __name__ == "__main__":
    update_channel_ids()
