import os
import time
from pathlib import Path

import requests

from paths import GENERATED_AUDIOS_DIR


XAI_TTS_URL = "https://api.x.ai/v1/tts"
MAX_TTS_CHARS = 15_000


def generate_audio(
    file_name,
    script,
    *,
    voice_id="eve",
    language="hi",
    codec="wav",
    sample_rate=24000,
    text_normalization=True,
    max_retries=3,
):
    if not script or not str(script).strip():
        raise ValueError("Script is empty. Cannot generate audio.")

    script = str(script).strip()
    if len(script) > MAX_TTS_CHARS:
        raise ValueError(
            f"xAI TTS input is {len(script)} characters; max is {MAX_TTS_CHARS}."
        )

    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY is not set.")

    payload = {
        "text": script,
        "voice_id": voice_id,
        "language": language,
        "output_format": {
            "codec": codec,
            "sample_rate": sample_rate,
        },
        "text_normalization": text_normalization,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = None
    for attempt in range(max_retries):
        response = requests.post(
            XAI_TTS_URL,
            headers=headers,
            json=payload,
            timeout=900,
        )

        if response.ok:
            break

        if response.status_code not in {429, 500, 503} or attempt == max_retries - 1:
            response.raise_for_status()

        time.sleep(2**attempt)

    if response is None:
        raise RuntimeError("No response received from xAI TTS.")

    GENERATED_AUDIOS_DIR.mkdir(parents=True, exist_ok=True)
    output_file = GENERATED_AUDIOS_DIR / f"{file_name}.{codec}"
    output_file.write_bytes(response.content)
    print(f"[INFO] Audio generated")

    return str(Path(output_file))
