import json
import os
from tasks.paths import GENERATED_TIMELINES_DIR

def build_timeline(file_name, chunks, duration):
    timeline = []
    duration = int(duration)

    parsed_chunks = []
    for chunk in chunks:
        try:
            start = to_seconds(chunk["start_timestamp"])
        except (KeyError, TypeError, ValueError):
            continue

        if start >= duration:
            continue

        parsed_chunks.append({
            "start": start,
            "text": chunk.get("text", "").strip(),
        })

    parsed_chunks.sort(key=lambda item: item["start"])

    for i, chunk in enumerate(parsed_chunks):
        start = chunk["start"]

        if i < len(parsed_chunks) - 1:
            next_start = parsed_chunks[i + 1]["start"]
            end = min(next_start, duration)
        else:
            end = duration

        if end <= start:
            continue

        timeline.append({
            "start": start,
            "end": end,
            "text": chunk["text"]
        })

    os.makedirs(GENERATED_TIMELINES_DIR, exist_ok=True)
    with open(GENERATED_TIMELINES_DIR / f"{file_name}.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=4)
    print(f"[INFO] Timeline saved")

    return timeline

def to_seconds(ts):
    mins, secs = map(int, ts.split(":"))
    return mins * 60 + secs
