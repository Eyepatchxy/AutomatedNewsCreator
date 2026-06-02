from dataclasses import dataclass
from enum import Enum
from typing import Any

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

@dataclass
class Stage:
    sr_no: int
    name: str
    weight: float
    progress: float = 0.0
    status: str = "pending"

    card: Any | None = None
    icon: Any | None = None
    label: Any | None = None

class VideoType(str, Enum):
    FULL = "Full"
    SHORT = "Short" 


class VideoDuration(Enum):
    SEC_30 = 30
    SEC_60 = 60
    SEC_90 = 90
    SEC_120 = 120