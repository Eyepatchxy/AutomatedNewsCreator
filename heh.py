from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
import os
from google import genai

api_key = "AIzaSyDOW6WXH4dYE8PnXRqBE3EFfvi-d12W02g"
client = genai.Client(api_key=api_key)
file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
previous_topics = ["US-China trade talks", "Apple's new iPhone release", "Global climate summit outcomes"]  

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
      "source": "...",
      "keywords": ["...", "..."]
    }
  ]
}

Constraints:
- Max 5 news items
- Summary must be 2-3 lines
- No duplicate or overlapping stories
- No explanations outside JSON
"""

print(instruction.replace("{previous_topics}","\n".join(previous_topics)))

try:
    if not api_key:
      raise Exception("GEMINI_API_KEY not found")
    
    

    prompt = instruction.format(
        previous_topics="/n".join(previous_topics)
    )

    # response = client.models.generate_content(
    #     model="gemini-3-flash-preview",
    #     contents=prompt
    # )

    # text = response

    # print (response)

except Exception as e:
    print(f"Error fetching news: {e}")