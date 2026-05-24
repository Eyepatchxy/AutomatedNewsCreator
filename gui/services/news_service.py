from gui.state.models import NewsItem
from paths import PROCESSED_NEWS_FILE
import json


def _news_title(item: dict) -> str:
    return (
        item.get("headline")
        or item.get("title")
        or item.get("topic")
        or item.get("cluster_topic")
        or ""
    )


def _news_description(item: dict) -> str:
    return (
        item.get("summary")
        or item.get("description")
        or item.get("news_description")
        or ""
    )


def load_processed_news() -> list[NewsItem]:
    fallback = [
        NewsItem(
            headline="India's AI policy debate intensifies as startups seek clearer rules",
            category="Technology",
            confidence=0.91,
            source_count=5,
            summary="A concise policy-focused update suitable for a short explainer.",
        ),
        NewsItem(
            headline="Markets open mixed as investors wait for inflation signals",
            category="Business",
            confidence=0.86,
            source_count=4,
            summary="A market brief with clear visual hooks and quick context.",
        ),
        NewsItem(
            headline="New climate report highlights urgent urban heat risks",
            category="Environment",
            confidence=0.88,
            source_count=6,
            summary="A data-led story that works well as a full-length video.",
        ),
    ]

    if not PROCESSED_NEWS_FILE.exists():
        return fallback

    try:
        data = json.loads(PROCESSED_NEWS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback

    if not data:
        return fallback

    items: list[NewsItem] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        headline = (
            item.get("headline")
            or item.get("title")
            or item.get("topic")
            or item.get("cluster_topic")
            or f"Processed news item {index + 1}"
        )
        category = item.get("category") or item.get("detected_category") or "General"
        confidence = float(item.get("confidence", item.get("score", 0.82)))
        source_count = int(item.get("source_count", len(item.get("sources", [])) or 1))
        summary = item.get("summary") or item.get("description") or item.get("news_description") or ""
        items.append(NewsItem(headline, category, confidence, source_count, summary))

    return items or fallback


def remove_processed_news(title: str, description: str = "") -> bool:
    if not PROCESSED_NEWS_FILE.exists():
        return False

    try:
        data = json.loads(PROCESSED_NEWS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False

    if not isinstance(data, list):
        return False

    clean_title = (title or "").strip().lower()
    clean_description = (description or "").strip().lower()
    removed = False
    remaining = []

    for item in data:
        if not isinstance(item, dict):
            remaining.append(item)
            continue

        item_title = _news_title(item).strip().lower()
        item_description = _news_description(item).strip().lower()
        title_matches = clean_title and item_title == clean_title
        description_matches = clean_description and item_description == clean_description

        if title_matches and (not clean_description or description_matches):
            removed = True
            continue

        remaining.append(item)

    if removed:
        PROCESSED_NEWS_FILE.write_text(
            json.dumps(remaining, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )

    return removed
