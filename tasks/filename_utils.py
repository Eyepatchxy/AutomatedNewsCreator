import re
from datetime import datetime


def slugify(text: str, fallback: str = "news-update", max_length: int = 60) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    if not text:
        text = fallback

    if len(text) <= max_length:
        return text

    trimmed = text[:max_length].strip("-")
    word_boundary = trimmed.rfind("-")
    if word_boundary > 0:
        trimmed = trimmed[:word_boundary]
    return trimmed or fallback


def build_file_name(title: str, created_at: datetime | None = None) -> str:
    created_at = created_at or datetime.now()
    timestamp = created_at.strftime("%Y-%m-%d_%H-%M-%S")
    print("[INFO] File name built")
    return f"{timestamp}_{slugify(title)}"
