import os
import time
from dotenv import load_dotenv
from google import genai
from groq import Groq
from paths import PROJECT_ROOT, GENERATED_SCRIPTS_DIR

load_dotenv(PROJECT_ROOT / ".env")

genai_api_key = os.getenv("GEMINI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

gemini_client = genai.Client(api_key=genai_api_key) if genai_api_key else None
groq_client = Groq(api_key=groq_api_key)

GEMINI_MODEL = os.getenv("SCRIPT_GENERATION_GEMINI_MODEL", "gemini-2.5-flash")
GROQ_MODEL = os.getenv("SCRIPT_GENERATION_GROQ_MODEL", "llama-3.3-70b-versatile")

instructions = """You are a script writer for a YouTube hindi news channel.
Your task is to convert the given news article into a clear and engaging hindi news script.

Structure:
- Start with channel intro with channel name. [Bee News Hindi]
- Then, give the news title as a headline.
- Next, narrate the news in a clear and engaging manner, using simple language suitable for a wide audience.
- Finally, end with a closing statement encouraging viewers to subscribe and stay tuned for more news updates.

STRICT RULES:
- Do NOT add any new facts
- Do NOT assume anything
- Only use information from the article
- If something is unclear, omit it
- Do NOT include any captions about music, scene changes, or visual elements
- Return the script as plain text, do add spaces and new lines for pauses, and necessary punctuation, but do NOT add any scene directions or captions.
- The script should be in natural spoken Hindi, not formal or literary Hindi.
- The script should be in devnagri script, not romanized Hindi.
- Do not use Latin/English letters in the script. Write borrowed English-origin words in Devanagari, e.g. "सब्सक्राइब", "लाइक", "डेडलाइन", "सीज़फायर".

Constraints:
- Write the script in natural spoken Hindi (not formal or literary Hindi)
- Use simple vocabulary suitable for news narration
- Avoid English words unless they are widely used in Hindi, and even then write them in Devanagari script.
- Do add punctation, conjunctions, and transition words to make the script feel natural and engaging
- Target a 90-second narrated video.
- Keep the script around 220 to 260 Hindi words.
- Use 8 to 11 short paragraphs so the narration has natural pauses.
- If the article has limited verified facts, still aim for at least 75 seconds, but do not add unverified facts or filler.
- Do not exaggerate or add unverified information
- Only include background or context if it is widely known and relevant
- Do not fabricate causes, impacts, or details
- Do not include scene directions (e.g., [Cut to...], [Music...])
- Start directly with a strong headline-style opening
- Avoid dramatic or exaggerated language
- Keep the tone professional and factual

Style:
- Use simple, clear language
- Write in a natural, spoken tone suitable for voice narration
- Keep it engaging but not clickbait

Article: 
"""

# def generate_script(file_name, article_text):
#     # article_text = " US-Iran two-week ceasefire: How Trump stepped back from brink, Pakistan’s role, and what comes next! After 39 days of war, the US and Iran have agreed to a temporary truce period during which the Strait of Hormuz will reopen. While this will come as a relief to the world, the negotiations over Iran's maximalist peace proposals will be the ultimate test of diplomatic skills. US President Donald Trump announced a two-week ceasefire with Iran just about an hour-and-a-half before his 8 pm (5.30 am IST) “deadline” ran out. Iranian Foreign Minister Seyed Abbas Araghchi swiftly agreed to the ceasefire around 40 minutes later. The announcements came after Pakistan Prime Minister Shehbaz Sharif, in a post on X, “requested” both countries to dial down the tensions. And so, 39 days since the war began, the world breathed a sigh of relief as the US President stepped back from the edge, just hours after threatening to destroy Iran’s energy infrastructure — and its “whole civilization” — if it did not reopen the Strait of Hormuz."

#     prompt = instructions + "\n" + article_text

#     
#     response = groq_client.chat.completions.create(
#     model=GROQ_MODEL,
#         messages=[
#             {"role": "user", "content": prompt}
#         ]
#     )    

#     script = response.choices[0].message.content

#     if script:

#         os.makedirs(GENERATED_SCRIPTS_DIR, exist_ok=True)
        
#         file_path = GENERATED_SCRIPTS_DIR / f"{file_name}.txt"
#         with open(file_path, "w", encoding="utf-8") as f:
#             f.write(script)

#     return script


def generate_with_gemini(prompt):

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
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
        timeout=60
    )

    return response.choices[0].message.content


def generate_script(file_name, article_text):

    prompt = instructions + "\n\n" + article_text

    script = None

    # Gemini retries
    for attempt in range(2):

        try:
            print(f"[INFO] Trying Gemini (attempt {attempt + 1})")

            script = generate_with_gemini(prompt)

            if script and script.strip():
                print("[INFO] Script generated using Gemini")
                break

        except Exception as e:
            print(f"[ERROR] Gemini failed: {e}")

            time.sleep(2)

    # Fallback to Groq
    if not script:

        try:
            print("[INFO] Falling back to Groq")

            script = generate_with_groq(prompt)

            print("[INFO] Script generated using Groq")

        except Exception as e:
            print(f"[ERROR] Groq also failed: {e}")
            return None

    # Save script
    if script:
        os.makedirs(GENERATED_SCRIPTS_DIR, exist_ok=True)

        file_path = GENERATED_SCRIPTS_DIR / f"{file_name}.txt"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(script)

    return script
