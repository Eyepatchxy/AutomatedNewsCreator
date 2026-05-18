import json

from tasks.ExtractionTools.channelwise_news_extractor import (
    create_youtube_client,
    get_channel_id_from_handle
)


def update_channel_ids(channels_file="channels.json"):

    youtube = create_youtube_client()

    # Load channels
    with open(channels_file, "r", encoding="utf-8") as f:
        channels = json.load(f)

    # Update IDs
    for channel in channels:

        handle = channel.get("handle")

        if not handle:
            continue

        print(f"Fetching ID for {handle}")

        channel_id = get_channel_id_from_handle(
            youtube,
            handle
        )

        if channel_id:
            channel["id"] = channel_id
            print(f"Updated: {handle}")
        else:
            print(f"Failed: {handle}")

    # Save updated JSON
    with open(channels_file, "w", encoding="utf-8") as f:
        json.dump(
            channels,
            f,
            indent=4,
            ensure_ascii=False
        )

    print("channels.json updated successfully.")


# Run
update_channel_ids()