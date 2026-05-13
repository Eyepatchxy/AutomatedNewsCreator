import json
import os
import time
from pathlib import Path

import requests

from tasks.paths import GENERATED_THUMBNAILS_DIR


XAI_IMAGE_URL = "https://api.x.ai/v1/images/generations"
DEFAULT_MODEL = "grok-imagine-image"
MAX_RETRIES = 3
DEFAULT_SIZE = "1792x1024"  # 1792×1024, 1280x720


def generate_thumbnail(
    file_name,
    *,
    model=DEFAULT_MODEL,
    size=DEFAULT_SIZE,
    image_format="png",
    max_retries=MAX_RETRIES,
):
    article_path = Path(f"Articles/{file_name}.json")

    if not article_path.exists():
        raise FileNotFoundError(f"Article file not found: {article_path}")

    with open(article_path, "r", encoding="utf-8") as article:
        article_data = json.load(article)

    news_type = article_data.get("type", "general")
    title = article_data.get("title", "").strip()

    keywords = article_data.get("keywords", [])
    keyword = keywords[0] if keywords else ""

    hook = article_data.get("hook", "").strip()
    hook = hook if hook else ""

    if not title:
        raise ValueError("Article title is missing.")

    api_key = os.getenv("XAI_API_KEY")

    if not api_key:
        raise ValueError("XAI_API_KEY is not set.")

    prompt = f"""
        Create a professional Hindi YouTube news thumbnail in modern Indian digital news style.

        News category: {news_type}
        News topic: {title}
        Main subject/entity: {keyword}

        Optional hook text (may or may not be used naturally):
        "{hook}"

        Style:
        Professional Indian news channel aesthetic, high CTR YouTube thumbnail, modern newsroom graphics, visually clean, emotionally engaging, premium editorial composition.

        Composition:
        One dominant focal subject.
        Relevant background scene connected to the news topic.
        Strong subject separation.
        Balanced layout with space for large Hindi text.
        Readable on mobile screens.

        Visual tone:
        Use colors and mood appropriate for the category:
        - Politics: deep reds, dark contrast, editorial seriousness
        - Tech: blue neon, modern UI elements, sleek lighting
        - Sports: dynamic motion and energetic composition
        - Business: clean professional financial-news look
        - International: world-news broadcast aesthetic
        - General news: modern TV newsroom style

        Text styling:
        Large bold Hindi headline area.
        Short impactful typography.
        Professional broadcast design.
        Do not overcrowd with text.

        Quality:
        Ultra detailed, sharp focus, cinematic lighting, realistic faces, high contrast, 16:9 aspect ratio, YouTube thumbnail optimized, premium digital news media quality.

        Avoid:
        Overcrowded composition, too many faces, unreadable text, distorted hands, low quality AI artifacts, fake-looking expressions, excessive clickbait, childish graphics.
        """.strip()

    payload = {
        "model": model,
        "prompt": prompt
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = None

    for attempt in range(max_retries):
        response = requests.post(
            XAI_IMAGE_URL,
            headers=headers,
            json=payload,
            timeout=300,
        )

        if response.ok:
            break

        if response.status_code not in {429, 500, 503} or attempt == max_retries - 1:
            response.raise_for_status()

        time.sleep(2**attempt)

    if response is None:
        raise RuntimeError("No response received from xAI image API.")

    data = response.json()

    image_url = (
        data.get("data", [{}])[0]
        .get("url")
    )

    if not image_url:
        raise ValueError("Image URL missing from xAI response.")

    image_response = requests.get(image_url, timeout=300)
    image_response.raise_for_status()

    GENERATED_THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

    output_file = GENERATED_THUMBNAILS_DIR / f"{file_name}.{image_format}"

    output_file.write_bytes(image_response.content)
    print("[INFO] Thumbnail generated")

    return str(output_file)