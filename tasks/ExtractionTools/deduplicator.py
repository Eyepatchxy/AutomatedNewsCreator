import re
import unicodedata
import json
import os
from pathlib import Path
from groq import Groq
from paths import (
    GENERATED_ARTICLES_DIR,
    RAW_NEWS_POOL_FILE,
    PROCESSED_NEWS_FILE,
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

def normalize_text(text):
    """
    Normalize text for deduplication.

    - lowercase
    - remove punctuation
    - remove emojis/symbols
    - normalize unicode
    - collapse extra spaces
    """

    if not text:
        return ""

    # Unicode normalization
    text = unicodedata.normalize("NFKD", text)

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove punctuation/symbols/emojis
    text = re.sub(r"[^\w\s]", " ", text)

    # Remove underscores
    text = text.replace("_", " ")

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def load_posted_articles(articles_dir=GENERATED_ARTICLES_DIR, limit=30):
    articles_dir = Path(articles_dir)

    if not articles_dir.exists():
        return []

    article_files = sorted(
        articles_dir.glob("*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

    posted_articles = []

    for article_file in article_files[:limit]:
        try:
            with open(article_file, "r", encoding="utf-8") as f:
                article = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Skipping posted article {article_file}: {e}")
            continue

        posted_articles.append({
            "title": article.get("title", ""),
            "details": article.get("details", "")[:500],
            "source": article.get("source", ""),
            "keywords": article.get("keywords", [])[:10],
        })

    return posted_articles


def load_json_list(path):
    path = Path(path)

    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return []

    return data if isinstance(data, list) else []


def semantic_deduplicate(
    input_file = RAW_NEWS_POOL_FILE,
    output_file = PROCESSED_NEWS_FILE,
    posted_articles_dir=GENERATED_ARTICLES_DIR,
    model=GROQ_MODEL
):
   
    videos = load_json_list(input_file)
    existing_processed_news = load_json_list(output_file)

    posted_articles = load_posted_articles(posted_articles_dir)

    
    client = Groq(api_key=GROQ_API_KEY)

    simplified_videos = []

    for idx, video in enumerate(videos):

        simplified_videos.append({
            "index": idx,
            "title": video.get("title", ""),
            "description": (
                video.get("description", "")[:300]
            ),
            "channel": video.get("channel", ""),
            "published_at": video.get(
                "published_at",
                ""
            ),
            "priority": video.get("priority", 999)
        })

    simplified_existing_news = []

    for idx, item in enumerate(existing_processed_news):

        simplified_existing_news.append({
            "index": idx,
            "cluster_topic": (
                item.get("cluster_topic")
                or item.get("title")
                or item.get("headline")
                or item.get("topic")
                or ""
            ),
            "news_description": (
                item.get("news_description")
                or item.get("description")
                or item.get("summary")
                or ""
            ),
            "priority": item.get("priority", 999),
        })

    # -----------------------------
    # Prompt
    # -----------------------------

    prompt = f"""
        You are a news deduplication system.

        Group input items that report
        the SAME news event/story.

        Rules:
        - The response should only be a JSON array of clusters, no explanations or extra text.
        - The raw input videos are newly fetched videos.
        - The existing processed news are stories already waiting in processed_news.json.
        - Deduplicate raw input videos and existing processed news together.
        - First compare every input item against already_posted_articles.
        - If an input item reports the same news event/story as an already posted article, exclude it completely.
        - Same posted story = same event, same announcement, same update, or no significant new development.
        - Only keep a posted-related story if the input clearly contains a significant new development after the posted article.
        - Same event = same cluster
        - Different wording = same cluster
        - Different opinions on same event = same cluster
        - Completely different events = separate clusters
        - Assign priority by ranking the final clusters from most important to least important.
        - Priority must be a compact sequence starting at 1 with no gaps.
        - If there are N clusters, priorities must be exactly 1 through N.
        - Response json should be sorted by priority in ascending order.
        - Use the input video's existing priority only as a tie breaker, not as the final priority value.
        - No 2 clusters should have the same priority number.

        Return ONLY valid JSON.

        Already posted articles:
        {json.dumps(posted_articles, indent=2, ensure_ascii=False)}

        Existing processed news:
        {json.dumps(simplified_existing_news, indent=2, ensure_ascii=False)}

        Raw input videos:
        {json.dumps(simplified_videos, indent=2)}

        Output format:
        [
        {{
            "topic": "short topic",
            "description": "short description of the news event",
            "priority": 1,
            "video_indexes": [0, 3] 
        }}
        ]
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    content = response.choices[0].message.content

    print("Deduplication response:")
    print(content)

    deduplicated = json.loads(content)

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            deduplicated,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Saved {len(deduplicated)} "
        f"deduplicated stories "
    )

    return deduplicated
