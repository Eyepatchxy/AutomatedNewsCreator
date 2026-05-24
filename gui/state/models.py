from dataclasses import dataclass

@dataclass
class NewsItem:
    headline: str
    category: str
    confidence: float
    source_count: int
    summary: str = ""

@dataclass
class Channel:
    name: str
    handle: str
    channel_id: str
    priority: int = 99