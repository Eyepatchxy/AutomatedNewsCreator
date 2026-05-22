from tasks.ExtractionTools.channelwise_news_extractor import (
    create_youtube_client,
    get_recent_videos,
)
from tasks.ExtractionTools.deduplicator import semantic_deduplicate


def run_extraction_pipeline(selected_channel_ids=None):
    youtube_client = create_youtube_client()
    get_recent_videos(youtube_client, selected_channel_ids=selected_channel_ids)
    return semantic_deduplicate()


if __name__ == "__main__":
    run_extraction_pipeline()
