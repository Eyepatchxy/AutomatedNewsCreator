from dotenv import load_dotenv
load_dotenv()

import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
from datetime import datetime
from tasks.news_extractor import get_news
from tasks.script_generator import generate_script
from tasks.chunk_generator import generate_chunks
from tasks.video_generator import generate_video
from tasks.paths import GENERATED_AUDIOS_DIR, GENERATED_CHUNKS_DIR

file_name = "test"  # datetime.now().strftime("%Y-%m-%d_%H-%M-%S_slug")
audio_file = GENERATED_AUDIOS_DIR / "heh.wav"

with open(GENERATED_CHUNKS_DIR / "2026-04-22_01-02-26.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)


# # Fetch news article
# article, news_count = get_news(file_name, previous_topics=[])

# article_title = article.get("title", "Untitled")
# article_details = article.get("details", "")
# article_type = article.get("type", "general")
# article_images = article.get("image_urls", [])
# article_source = article.get("source", "Unknown")
# article_keywords = article.get("keywords", [])

# # Generate script
# script = generate_script(file_name, article_details)

# # Generate chunks
# chunks = generate_chunks(file_name, script)

# # Generate audio
# audio_file = generate_audio(file_name, script)

# Generate video
video_file = generate_video(file_name, chunks, str(audio_file))
