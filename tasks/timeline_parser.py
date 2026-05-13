import json
import os
from tasks.paths import GENERATED_TIMELINES_DIR

def build_timeline(file_name, chunks, duration):
    timeline = []

    for i in range(len(chunks)):
        start = to_seconds(chunks[i]["start_timestamp"])

        if i < len(chunks) - 1:
            next_start = to_seconds(chunks[i+1]["start_timestamp"])
            end = next_start - 1
        else:
            end = duration  # ✅ no conversion

        timeline.append({
            "start": start,
            "end": end,
            "text": chunks[i]["text"]
        })

    os.makedirs(GENERATED_TIMELINES_DIR, exist_ok=True)
    with open(GENERATED_TIMELINES_DIR / f"{file_name}.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=4)
    print(f"[INFO] Timeline saved")

    return timeline

def to_seconds(ts):
    mins, secs = map(int, ts.split(":"))
    return mins * 60 + secs
