import json
import os
from google import genai
from google.genai import types
from tasks.paths import PROCESSED_NEWS_FILE, PENDING_ARTICLES_DIR
from tasks.filename_utils import build_file_name

INPUT_FILE = PROCESSED_NEWS_FILE
OUTPUT_DIR = PENDING_ARTICLES_DIR 


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def verify_news(
    input_file=INPUT_FILE,
):
    with open(input_file, "r", encoding="utf-8") as f:
        news_items = json.load(f)

    if not news_items:
        print("No news items found")
        return None

    # Get item with highest priority
    # (lowest priority number)
    top_item = min(
        news_items,
        key=lambda x: x.get("priority", 9999)
    )

    title = top_item.get("title") or top_item.get("cluster_topic", "")
    description = (
        top_item.get("description")
        or top_item.get("news_description", "")
    )

    # Remove processed item
    updated_news_items = [
        item
        for item in news_items
        if item != top_item
    ]

    # Replace original list
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(
            updated_news_items,
            f,
            indent=4,
            ensure_ascii=False
        )

    prompt = f"""
        You are a professional news verification system.

        Your task:
        1. Verify whether this news is true using online information.
        2. Ignore clickbait or exaggerated wording.
        3. Summarize the verified facts neutrally.
        4. If uncertain, mention uncertainty clearly.
        5. Return STRICT JSON ONLY.
        6. "isTrue" should be strictly boolean, not string.

        News Title: {title}

        News Description: {description}

        Output format (STRICT JSON):
        {{
        "articles": [
            {{
            "title": "...",
            "title_hi": "...",
            "details": "...",
            "type": "politics/tech/business/global",
            "hook": "...",
            "source": "...",
            "keywords": ["...", "..."],
            "isTrue": true
            }}
        ]
        }}
    """

    if not title:
        print("No priority 1 news found")
        return None

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
            tools=[
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ]
        )
    )

    try:

        parsed_json = json.loads(response.text)

        for article in parsed_json.get("articles", []):

            if article.get("isTrue"):

                file_name = build_file_name(article.get("title", "news-update"))
                save_article(file_name, article)        

       
        return parsed_json

    except Exception as e:

        print("Failed to parse/save JSON")
        print("Error:", e)
        print(response.text)

        return None
    

def save_article(file_name, article, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)

    with open(
        os.path.join(output_dir, f"{file_name}.json"),
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            article,
            f,
            ensure_ascii=False,
            indent=2
        )
