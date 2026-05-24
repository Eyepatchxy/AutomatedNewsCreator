import json

from paths import TOKEN_FILE


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

    if not lookup_value:
        return None

    lookups = (
        {"forHandle": lookup_value},
        {"forUsername": lookup_value},
    )

    for lookup in lookups:
        try:
            response = youtube.channels().list(
                part="id,snippet",
                **lookup,
            ).execute()
        except Exception:
            continue

        items = response.get("items", [])
        if not items:
            continue

        item = items[0]
        snippet = item.get("snippet", {})
        handle = snippet.get("customUrl") or cleaned
        if handle and not handle.startswith("@"):
            handle = f"@{handle}"

        return {
            "id": item["id"],
            "name": snippet.get("title") or handle or cleaned,
            "handle": handle,
        }

    print(f"Channel not found: {identifier}")
    return None


def get_channel_id(identifier: str) -> str | None:
    metadata = get_channel_metadata(identifier)
    return metadata["id"] if metadata else None


def update_channel_ids(channels_file="channels.json"):

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
