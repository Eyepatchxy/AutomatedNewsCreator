from gui.state.app_state import STATE
from gui.state.models import Channel
from paths import CHANNELS_FILE
from tasks.ExtractionTools.channelId_extractor import get_channel_metadata
import json


def _load_channel_data() -> dict:
    if not CHANNELS_FILE.exists():
        return {"channels": []}

    try:
        data = json.loads(CHANNELS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"channels": []}

    if isinstance(data, list):
        return {"channels": data}

    channels = data.get("channels", [])
    if not isinstance(channels, list):
        channels = []

    return {**data, "channels": channels}


def _normalize_priorities(channels: list[dict]) -> list[dict]:
    sorted_channels = sorted(
        channels,
        key=lambda item: (
            int(item.get("priority", 9999)),
            item.get("name", ""),
            item.get("handle", ""),
        ),
    )

    for index, channel in enumerate(sorted_channels, start=1):
        channel["priority"] = index

    return sorted_channels


def _save_channel_data(data: dict) -> None:
    data["channels"] = _normalize_priorities(data.get("channels", []))
    CHANNELS_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHANNELS_FILE.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def load_channels() -> list[Channel]:
    data = _load_channel_data()
    channels = data["channels"]
    return [
        Channel(
            name=item.get("name", "Unnamed channel"),
            handle=item.get("handle", ""),
            channel_id=item.get("id", item.get("channel_id", "")),
            priority=item.get("priority", 99),
        )
        for item in channels
    ]


def next_priority_slot() -> int:
    used_priorities = {
        int(channel.priority)
        for channel in load_channels()
        if int(channel.priority) > 0
    }

    priority = 1
    while priority in used_priorities:
        priority += 1

    return priority


def priority_choices() -> list[int]:
    channels = load_channels()
    return list(range(1, len(channels) + 2))


def add_channel(identifier: str, priority: int | None = None) -> Channel:
    metadata = get_channel_metadata(identifier)
    if not metadata:
        raise ValueError("Channel not found. Check the YouTube handle or username.")

    data = _load_channel_data()
    channels = _normalize_priorities(data["channels"])

    normalized_handle = metadata["handle"].lower()
    channel_id = metadata["id"]

    if any(item.get("id") == channel_id for item in channels):
        raise ValueError("That channel is already in channels.json.")

    if any((item.get("handle") or "").lower() == normalized_handle for item in channels):
        raise ValueError("That handle is already in channels.json.")

    target_priority = priority or next_priority_slot()
    target_priority = max(1, min(int(target_priority), len(channels) + 1))

    for channel in channels:
        if int(channel.get("priority", 9999)) >= target_priority:
            channel["priority"] = int(channel.get("priority", 9999)) + 1

    new_channel = {
        "priority": target_priority,
        "name": metadata["name"],
        "handle": metadata["handle"],
        "id": channel_id,
    }
    channels.append(new_channel)
    data["channels"] = channels
    _save_channel_data(data)

    return Channel(
        name=new_channel["name"],
        handle=new_channel["handle"],
        channel_id=new_channel["id"],
        priority=new_channel["priority"],
    )


def selected_channel_names() -> list[str]:
    ids = set(STATE["selected_channels"])
    return [channel.name for channel in load_channels() if channel.channel_id in ids]


def selected_channel_priorities() -> list[int]:
    ids = set(STATE["selected_channels"])
    return [
        int(channel.priority)
        for channel in load_channels()
        if channel.channel_id in ids
    ]
