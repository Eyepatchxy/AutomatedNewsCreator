import json
from datetime import datetime
import time
import os
from urllib import response
from google import genai

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

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

Output format (STRICT JSON):
{
  "news": [
    {
      "title": "...",
      "details": "...",
      "type": "politics/tech/business/global",
      "image_urls": ["...", "..."],
      "source": "...",
      "keywords": ["...", "..."]
    }
  ]
}

Constraints:
- Only return one news item.
- Summary must be 2-3 lines
- No duplicate or overlapping stories
- No explanations outside JSON
"""

def get_news(file_name, previous_topics):
    for attempt in range(5):
        try:
            if not api_key:
                raise Exception("GEMINI_API_KEY not found")

            prompt = instruction.replace("{previous_topics}","\n".join(previous_topics))

            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )

            text = response.text

            if text == None:
                raise Exception("No response from API")
            
            text = text.strip()

            # 🔹 Handle possible markdown wrapping
            if text.startswith("```"):
                text = text.split("```")[1]
            
            data = json.loads(text)

            news_list = data.get("news", [])
            if not news_list:
                raise Exception("No news returned")
            
            os.makedirs("Articles", exist_ok=True)
            i = 0
            while i < len(news_list):
                with open(f"Articles/{file_name}_{i + 1}.json", "w") as f:
                    json.dump(news_list[i], f, indent=2)
                i += 1

            return news_list[0], len(news_list)

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    raise Exception("Failed to fetch news after multiple attempts")