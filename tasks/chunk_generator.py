import json
import os
from dotenv import load_dotenv
from groq import Groq
from paths import PROJECT_ROOT, GENERATED_CHUNKS_DIR
from gui.components.progress_pipeline import ProgressPipeline

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("GROQ_API_KEY")
CHUNK_GENERATION_GROQ_MODEL = os.getenv(
    "CHUNK_GENERATION_GROQ_MODEL",
    "llama-3.3-70b-versatile",
)

client = Groq(api_key=api_key)

instructions = """Analyze the given script and generate text string which represent parts of the script.
When the script is converted to audio and played, these text strings should be able to be used as captions for the audio.
Also, generate the estimate start timestamp for each text string when the script starts talking about the corresponding text string.

You must return ONLY valid JSON.

No natural language.
No introduction.
No explanation.

If the output is not valid JSON, it will be rejected.

Format:
[
  {
    "start_timestamp": "mm:ss",
    "end_timestamp": "mm:ss",
    "text": "..."
  },
]

Constraints:
- The text strings should be concise and capture the essence of the corresponding part of the script.
- The text strings should be in either Devanagari, and may contain few English words for convenience.
- The text strings should be suitable for use as captions, so they should be clear and easy to read.
- The estimated timestamps should be in the format "mm:ss" and should be based on the assumption that the script is narrated at a natural pace.
- Return the output as a list of dictionaries, where each dictionary has two keys: "start_timestamp" and "text". 
- The "start_timestamp" key should have the estimated start timestamp for the corresponding text string, and the "text" key should have the corresponding text string.

Script:

"""

def generate_chunks(file_name, script, pipeline:ProgressPipeline, duration=None):
    pipeline.start_stage(4)

    prompt = instructions + "\n" + script
    if duration:
        prompt += (
            "\n\nAudio duration constraint:\n"
            f"- The final audio is {int(duration)} seconds long.\n"
            "- Do not create any start_timestamp at or after the audio duration.\n"
            "- The final caption should start before the audio ends.\n"
            "- Spread captions naturally across the full audio duration.\n"
        )

    response = client.chat.completions.create(
        model=CHUNK_GENERATION_GROQ_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    chunks = response.choices[0].message.content    

    if chunks is None:
        print("Failed to generate chunks.")
        return None    

    if isinstance(chunks, str):
        chunks_text = chunks.strip()

        if chunks_text.startswith("```"):
            parts = chunks_text.split("```")
            chunks_text = parts[1] if len(parts) > 1 else chunks_text
            if chunks_text.startswith("json"):
                chunks_text = chunks_text[4:].strip()

        chunks = json.loads(chunks_text)

    os.makedirs(GENERATED_CHUNKS_DIR, exist_ok=True)
    with open(GENERATED_CHUNKS_DIR / f"{file_name}.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Chunks saved")

    pipeline.complete_stage(4)

    return chunks
