import json
import time
import os
from google import genai
from tasks.paths import ARTICLES_DIR

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

instruction = """You are a news aggregation system.

Your task is to return the latest, important, and NON-REPEATED news.

Context:
Previously covered topics:
{previous_topics}

Instructions:
1. Do NOT repeat any news that matches or is similar to previously covered topics.
2. If a story is an update, include ONLY if there is a significant new development.
3. Prioritize fresh, high-impact, and diverse topics (politics, tech, business, global).
4. Avoid minor or redundant news.
5. Each news item must be clearly distinct.
6. Do prioritize news that has significant implications or widespread interest.
7. Order keywords by relevance to the main news topic.

Output format (STRICT JSON):
{
  "news": [
    {
      "title": "...",
      "details": "...",
      "type": "politics/tech/business/global",
      "hook": ["..."],
      "source": "...",
      "keywords": ["...", "..."]
    }
  ]
}

Constraints:
- Only return one news item.
- Hook must be a one short hindi sentence that sounds interesting and makes people want to read the article.
- No duplicate or overlapping stories
- No explanations outside JSON
"""


def parse_news_response(text):
    text = text.strip()

    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        text = text.strip()

    if text.startswith("json"):
        text = text[4:].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise

        return json.loads(text[start:end + 1])


def save_article(file_name, article):
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    with open(ARTICLES_DIR / f"{file_name}.json", "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)


def get_news(file_name=None, previous_topics=None):
    previous_topics = previous_topics or []
    for attempt in range(5):
        try:
            if not api_key:
                raise Exception("GEMINI_API_KEY not found")

            prompt = instruction.replace("{previous_topics}", "\n".join(previous_topics))

            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )

            text = response.text
            # print("Raw news response:", text)

            if text is None:
                raise Exception("No response from API")

            data = parse_news_response(text)

            news_list = data.get("news", [])
            if not news_list:
                raise Exception("No news returned")

            if file_name:
                save_article(file_name, news_list[0])

            return news_list[0], len(news_list)

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    raise Exception("Failed to fetch news after multiple attempts")
