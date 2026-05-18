import json
import time
from tasks.ExtractionTools.channelwise_news_extractor import (
    create_youtube_client,
    get_recent_videos,
)
from tasks.ExtractionTools.deduplicator import semantic_deduplicate
from tasks.ExtractionTools.news_verifier import verify_news

youtube_client = create_youtube_client()

get_recent_videos(youtube_client)
semantic_deduplicate()
verify_news()



# def _is_previous_topic(story, previous_topics):
#     if not previous_topics:
#         return False

#     story_text = normalize_text(
#         " ".join(
#             [
#                 story.get("cluster_topic", ""),
#                 story.get("news_description", ""),
#                 story.get("title", ""),
#                 story.get("description", ""),
#             ]
#         )
#     )

#     for topic in previous_topics:
#         previous_topic = normalize_text(topic)
#         if previous_topic and previous_topic in story_text:
#             return True

#     return False


# def _filter_previous_topics(stories, previous_topics):
#     if not previous_topics:
#         return stories

#     return [
#         story
#         for story in stories
#         if not _is_previous_topic(story, previous_topics)
#     ]


# def _save_processed_stories(stories):
#     PROCESSED_NEWS_FILE.parent.mkdir(parents=True, exist_ok=True)

#     with open(PROCESSED_NEWS_FILE, "w", encoding="utf-8") as f:
#         json.dump(stories, f, indent=4, ensure_ascii=False)


# def _extract_verified_article(verified_data):
#     if not verified_data:
#         return None

#     for article in verified_data.get("articles", []):
#         if article.get("isTrue"):
#             return article

#     return None
