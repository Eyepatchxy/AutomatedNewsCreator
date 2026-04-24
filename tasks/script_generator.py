import os
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

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

Constraints:
- Write the script in natural spoken Hindi (not formal or literary Hindi)
- Use simple vocabulary suitable for news narration
- Avoid English words unless they are widely used in Hindi (e.g., "deadline", "ceasefire")
- Do add punctation, conjunctions, and transition words to make the script feel natural and engaging
- Keep the script between 250 and 1000 words (approx. 2-8 minutes)
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

def generate_script(file_name, article_text):
    # article_text = " US-Iran two-week ceasefire: How Trump stepped back from brink, Pakistan’s role, and what comes next! After 39 days of war, the US and Iran have agreed to a temporary truce period during which the Strait of Hormuz will reopen. While this will come as a relief to the world, the negotiations over Iran's maximalist peace proposals will be the ultimate test of diplomatic skills. US President Donald Trump announced a two-week ceasefire with Iran just about an hour-and-a-half before his 8 pm (5.30 am IST) “deadline” ran out. Iranian Foreign Minister Seyed Abbas Araghchi swiftly agreed to the ceasefire around 40 minutes later. The announcements came after Pakistan Prime Minister Shehbaz Sharif, in a post on X, “requested” both countries to dial down the tensions. And so, 39 days since the war began, the world breathed a sigh of relief as the US President stepped back from the edge, just hours after threatening to destroy Iran’s energy infrastructure — and its “whole civilization” — if it did not reopen the Strait of Hormuz."

    prompt = instructions + "\n" + article_text

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    script = response.choices[0].message.content

    if script:

        os.makedirs("GeneratedScripts", exist_ok=True)
        
        file_path = f"GeneratedScripts/{file_name}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(script)

    return script