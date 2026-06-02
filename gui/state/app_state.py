from typing import Any
from gui.state.models import VideoDuration, VideoType


STATE: dict[str, Any] = {
    "selected_channels": [],
    "selected_news": None,
    "custom_topic": None,
    "channel_flash": None,
    "extraction_job": None,
    "video_job": None,
    "video_type": VideoType.FULL,
    "upload_job": True,
    "layout": None,
    "target_time": VideoDuration.SEC_90
}
