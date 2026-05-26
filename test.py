import json
import os
import sys
from pathlib import Path


FILE_NAME = "2026-05-24_21-06-01_iran-nuclear-deal"
HEADLINE = "इरान परमाणु समझौता"
FONT_PATH = "/home/eyepatchxy/.local/share/noto-sans-devanagari/NotoSansDevanagari-Bold.ttf"


def main() -> None:
    file_name = sys.argv[1] if len(sys.argv) > 1 else FILE_NAME

    if Path(FONT_PATH).exists():
        os.environ.setdefault("VIDEO_TEXT_FONT", FONT_PATH)

    from tasks.video_generator import generate_video

    chunks_file = Path("Generated/Chunks") / f"{file_name}.json"
    audio_file = Path("Generated/Audios") / f"{file_name}.wav"

    chunks = json.loads(chunks_file.read_text(encoding="utf-8"))
    output_file = generate_video(file_name, chunks, audio_file, HEADLINE)

    print(output_file)


if __name__ == "__main__":
    main()
