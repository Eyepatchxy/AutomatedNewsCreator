import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from groq import Groq
from paths import PROJECT_ROOT, PROCESSED_NEWS_FILE, GENERATED_ARTICLES_DIR
from tasks.filename_utils import build_file_name

load_dotenv(PROJECT_ROOT / ".env")

INPUT_FILE = PROCESSED_NEWS_FILE
OUTPUT_DIR = GENERATED_ARTICLES_DIR 
GEMINI_MODEL = os.getenv("NEWS_VERIFICATION_GEMINI_MODEL", "gemini-1.5-flash")
GROQ_MODEL = os.getenv("NEWS_VERIFICATION_GROQ_MODEL", "llama-3.3-70b-versatile")


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_with_gemini(prompt):
    response = client.models.generate_content(
        model=GEMINI_MODEL,
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
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
        timeout=60
    )

    return response.choices[0].message.content


def verify_news(
    title = "",
    description = "",
):
    
    prompt = f"""
        You are a professional news verification system.

        Your task:
        1. Verify whether this news is true using online information.
        2. Ignore clickbait or exaggerated wording.
        3. Summarize the verified facts neutrally.
        4. If uncertain, mention uncertainty clearly.
        5. Return STRICT JSON ONLY.
        6. "isTrue" should be strictly boolean, not string.
        7. If title and description are insufficient for verification, use the Google Search tool to find more information. Only include facts that can be verified with high confidence.
        8. If title and description are blank, empty or cannot be interpreted, you may search the web for recent news and verify one of them, but only if you can find a well-verified news story with enough information to create a detailed summary. The type priority should be: global > politics > tech etc.

        News Title: {title}

        News Description: {description}

        Output format (STRICT JSON):
        {{
        "article": 
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
        }}
    """

    if not title:
        print("[INFO] No title passed into verify_news; attempting quick generation.")

    response_text = None

    try:
        response_text = generate_with_gemini(prompt)
        parsed_json = json.loads(response_text)
    except Exception as e:
        print("Gemini failed, falling back to Groq")
        print("Error:", e)

        try:
            response_text = generate_with_groq(prompt)
            parsed_json = json.loads(response_text)
        except Exception as groq_error:
            print("Groq also failed")
            print("Error:", groq_error)
            if response_text:
                print(response_text)
            return None

    try:

        saved_article = False

        article = parsed_json.get("article")
        if article and article.get("isTrue"):
            
            file_name = build_file_name(article.get("title", "news-update"))
            article["file_name"] = file_name
            article.setdefault("uploaded", False)
            save_article(file_name, article)
            saved_article = True
        
        if saved_article:
            print(f"[INFO] Article verified and saved: {article['title']}")

            return file_name
        else:
            print(f"[INFO] Article did not pass verification: {article['title'] if article else 'No article data'}")


    except Exception as e:

        print("[INFO] Failed to Generate Article")
        print("Error:", e)
        print(response_text)

        return None
    

def save_article(file_name, article, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    article_to_save = dict(article)
    article_to_save.setdefault("file_name", file_name)
    article_to_save.setdefault("uploaded", False)
    article_to_save["keywords"] = [
        f"#{str(keyword).strip().lstrip('#')}"
        for keyword in article_to_save.get("keywords", [])
        if str(keyword).strip()
    ]

    with open(
        os.path.join(output_dir, f"{file_name}.json"),
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            article_to_save,
            f,
            ensure_ascii=False,
            indent=2
        )
