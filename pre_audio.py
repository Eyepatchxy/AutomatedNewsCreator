from dotenv import load_dotenv
load_dotenv()

from tasks.news_extractor import get_news, save_article
from tasks.script_generator import generate_script
from tasks.chunk_generator import generate_chunks
from tasks.filename_utils import build_file_name
from tasks.paths import GENERATED_AUDIOS_DIR, GENERATED_CHUNKS_DIR, GENERATED_SCRIPTS_DIR


def main():
    article, _ = get_news(previous_topics=[])
    file_name = build_file_name(article.get("title", "news-update"))
    save_article(file_name, article)
    article_details = article.get("details", "")

    script = generate_script(file_name, article_details)
    generate_chunks(file_name, script)

    print("Pre-audio stage complete.")
    print(f"Filename: {file_name}")
    print(f"Script: {GENERATED_SCRIPTS_DIR / f'{file_name}.txt'}")
    print(f"Chunks: {GENERATED_CHUNKS_DIR / f'{file_name}.json'}")
    print(f"Place the audio file at: {GENERATED_AUDIOS_DIR / f'{file_name}.wav'}")
    print(f"Then run: python post_audio.py {file_name}")


if __name__ == "__main__":
    main()
