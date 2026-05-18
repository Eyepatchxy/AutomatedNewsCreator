import json
import os
from google import genai
from google.genai import types
from tasks.filename_utils import build_file_name
from tasks.ExtractionTools.news_verifier import save_article


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def topicwise_news_extractor(title, description):

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
