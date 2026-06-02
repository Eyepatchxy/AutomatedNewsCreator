import json
import os
import time
from dotenv import load_dotenv
from google import genai
from groq import Groq
from google.genai import types
from paths import PROJECT_ROOT
from tasks.filename_utils import build_file_name
from tasks.news_verifier import save_article

load_dotenv(PROJECT_ROOT / ".env")

TOPICWISE_NEWS_GEMINI_MODEL = os.getenv("TOPICWISE_NEWS_GEMINI_MODEL", "gemini-2.5-pro")
TOPICWISE_NEWS_GROQ_MODEL = os.getenv("TOPICWISE_NEWS_GROQ_MODEL", "llama-3.3-70b-versatile")

gemini_api_key = os.getenv("GEMINI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

gemini_client = genai.Client(api_key=gemini_api_key)
groq_client = Groq(api_key=groq_api_key)

def generate_with_gemini(prompt):

    response = gemini_client.models.generate_content(
        model=TOPICWISE_NEWS_GEMINI_MODEL,
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

    return response.text


def generate_with_groq(prompt):

    response = groq_client.chat.completions.create(
        model=TOPICWISE_NEWS_GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        timeout=60,
    )

    return response.choices[0].message.content

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
            "details": "A factual verified summary with enough concrete context for a 75-90 second Hindi news script. Include only verified facts, key people/organizations, location, what happened, and current status. Do not add speculation.",
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

    response_text = None

    # Gemini 
    try:

        print(f"[INFO] Trying Gemini")

        response_text = generate_with_gemini(prompt)

        if response_text and response_text.strip():

            print("[INFO] Verification completed using Gemini")

    except Exception as e:

        print(f"[ERROR] Gemini failed: {e}")


    # Groq fallback
    if not response_text:

        try:

            print("[INFO] Falling back to Groq")

            response_text = generate_with_groq(prompt)

            print("[INFO] Verification completed using Groq")

        except Exception as e:

            print(f"[ERROR] Groq also failed: {e}")

            return None

    try:

        parsed_json = json.loads(response_text)

        for article in parsed_json.get("articles", []):

            if article.get("isTrue"):

                file_name = build_file_name(article.get("title", "news-update"))
                article["file_name"] = file_name
                save_article(file_name, article)        

       
        return parsed_json

    except Exception as e:

        print("Failed to parse/save JSON")
        print("Error:", e)
        print(response_text)

        return None
