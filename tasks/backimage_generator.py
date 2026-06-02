import json
import math
import os
import time

import requests
from dotenv import load_dotenv

from paths import PROJECT_ROOT, GENERATED_ARTICLES_DIR, GENERATED_BACKIMAGES_DIR
from gui.components.progress_pipeline import ProgressPipeline
from gui.state.models import VideoType

load_dotenv(PROJECT_ROOT / ".env")

XAI_IMAGE_URL = "https://api.x.ai/v1/images/generations"

DEFAULT_MODEL = os.getenv("BACKIMAGE_IMAGE_MODEL", "grok-imagine-image")
DEFAULT_SIZE = "1792x1024"

MAX_RETRIES = 3
MAX_IMAGES = 4
DURATION_PER_IMAGE = 30


def get_window_text(
    timeline,
    window_start,
    window_end,
):
    texts = []

    for item in timeline:

        item_start = item.get("start", 0)
        item_end = item.get("end", 0)

        overlaps = (
            item_start < window_end
            and item_end > window_start
        )

        if overlaps:

            text = item.get("text", "").strip()

            if text:
                texts.append(text)

    return " ".join(texts)


def generate_backimages(
    file_name,
    timeline,
    duration,
    pipeline:ProgressPipeline,
    video_type: VideoType = VideoType.FULL,
    model=DEFAULT_MODEL,
    image_format="png",
    max_retries=MAX_RETRIES,
):
    pipeline.start_stage(7)

    article_path = GENERATED_ARTICLES_DIR / f"{file_name}.json"

    if not article_path.exists():
        raise FileNotFoundError(
            f"Article file not found: {article_path}"
        )

    with open(article_path, "r", encoding="utf-8") as article_file:
        article_data = json.load(article_file)

    title = article_data.get("title", "").strip()
    news_type = (article_data.get("type") or "general").strip()

    keywords = article_data.get("keywords", [])
    keyword = keywords[0] if keywords else ""

    if not title:
        raise ValueError("Article title is missing.")

    api_key = os.getenv("XAI_API_KEY")

    if not api_key:
        raise ValueError("XAI_API_KEY is not set.")

    if video_type == VideoType.SHORT:
        format_requirements = """
        Format requirements:
        STRICT vertical 9:16 image for a YouTube Shorts video.
        Portrait composition only.
        Do not create a horizontal, square, or 16:9 image.
        Keep important subjects centered and safe for a 1080x1920 vertical frame.
        Leave clear vertical-safe space for subtitles and overlays.
        """.strip()
    else:
        format_requirements = """
        Format requirements:
        STRICT horizontal 16:9 image for a normal YouTube video.
        Landscape composition only.
        Do not create a vertical, square, or 9:16 image.
        Keep important subjects safe for a 1920x1080 horizontal frame.
        Leave clear horizontal-safe space for subtitles and overlays.
        """.strip()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    image_count = min(
        MAX_IMAGES,
        max(
            1,
            math.ceil(duration / DURATION_PER_IMAGE)
        )
    )

    output_dir = GENERATED_BACKIMAGES_DIR / file_name
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_images = []

    for index in range(image_count):

        window_start = (
            index * DURATION_PER_IMAGE
        )

        window_end = (
            window_start + DURATION_PER_IMAGE
        )

        scene_text = get_window_text(
            timeline,
            window_start,
            window_end,
        )

        prompt = f"""
        Create a cinematic background image
        for a Hindi news video.

        News category:
        {news_type}

        News title:
        {title}

        Main subject:
        {keyword}

        Scene context:
        {scene_text}

        Scene number:
        {index + 1}

        Style:
        Realistic cinematic journalism style.
        Professional news atmosphere.
        High-quality editorial visual design.

        Composition:
        One clear focal subject.
        Strong visual storytelling.
        Balanced composition.
        Space for subtitles and overlays.
        Mobile-friendly readability.

        {format_requirements}

        Quality:
        Ultra detailed.
        Cinematic lighting.
        Realistic textures.
        Sharp focus.
        High contrast.
        Professional digital media quality.

        Important:
        No text.
        No logos.
        No watermarks.
        No split-screen collages.
        No channel branding.

        Avoid:
        Distorted hands.
        Distorted faces.
        AI artifacts.
        Unrealistic anatomy.
        Cartoon style.
        Overcrowded scenes.
        """.strip()

        payload = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "response_format": "url"
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

            retryable_status_codes = {
                429,
                500,
                503,
            }

            should_retry = (
                response.status_code
                in retryable_status_codes
            )

            is_last_attempt = (
                attempt == max_retries - 1
            )

            if (
                not should_retry
                or is_last_attempt
            ):
                response.raise_for_status()

            pipeline.update_stage_progress(7, index/image_count)

            time.sleep(2 ** attempt)

        if response is None:
            raise RuntimeError(
                "No response received from xAI API."
            )

        data = response.json()

        image_url = (
            data.get("data", [{}])[0]
            .get("url")
        )

        if not image_url:
            raise ValueError(
                f"Image URL missing for image {index + 1}."
            )

        image_response = requests.get(
            image_url,
            timeout=300,
        )

        image_response.raise_for_status()

        output_file = (
            output_dir
            / f"img{index + 1}.{image_format}"
        )

        output_file.write_bytes(
            image_response.content
        )

        generated_images.append(
            str(output_file)
        )
        print(f"[INFO] Generated backimage {index + 1}/{image_count}")

    pipeline.complete_stage(7)

    return generated_images
