from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    concatenate_videoclips,
    vfx
)

import os
import json
import math
from dotenv import load_dotenv

from paths import PROJECT_ROOT, GENERATED_BACKIMAGES_DIR, GENERATED_VIDEOS_DIR
from tasks.timeline_parser import build_timeline

load_dotenv(PROJECT_ROOT / ".env")

DURATION_PER_IMAGE = 30

FONT_PATH = os.getenv("VIDEO_TEXT_FONT", "Noto Sans Devanagari")


def create_background(file_name, duration):

    folder = GENERATED_BACKIMAGES_DIR / file_name

    images = sorted(folder.glob("*.png"))

    fallback = GENERATED_BACKIMAGES_DIR / "Fallback.jpg"

    clips = []

    total_segments = math.ceil(duration / DURATION_PER_IMAGE)

    for i in range(total_segments):

        start = i * DURATION_PER_IMAGE
        remaining = duration - start
        clip_duration = min(DURATION_PER_IMAGE, remaining)

        # pick image or fallback
        if images:
            img = images[i % len(images)]
        else:
            img = fallback

        if not img.exists():
            raise FileNotFoundError(
                f"Neither generated images nor fallback found: {fallback}"
            )

        clip = (
            ImageClip(str(img))
            .with_duration(clip_duration)
            .resized((1920, 1080))
            .resized(lambda t: 1 + 0.03 * t)

        )

        clips.append(clip)

    return concatenate_videoclips(clips, method="compose").with_duration(duration)


def generate_video(file_name, chunks, audio_file, headline_text="BREAKING NEWS"):

    if isinstance(chunks, str):
        chunks = json.loads(chunks)

    audio = AudioFileClip(str(audio_file))
    duration = math.ceil(audio.duration)

    background = create_background(file_name, duration)

    timeline = build_timeline(file_name, chunks, duration)

    headline = (
        TextClip(
            text=headline_text,
            font_size=65,
            font=FONT_PATH,
            color="white",
            method="caption",
            size=(1800, 180),
            stroke_color="black",
            stroke_width=2,
            text_align="center",
        )
        .with_position(("center", 10))
        .with_duration(duration)
    )

    text_clips = []

    for chunk in timeline:
        chunk_duration = chunk["end"] - chunk["start"]
        if chunk_duration <= 0:
            continue

        subtitle = (
            TextClip(
                text=chunk["text"],
                font_size=56,
                font=FONT_PATH,
                color="white",
                size=(1820, 520),
                method="caption",
                stroke_color="black",
                stroke_width=3,
            )
            .with_position(
                lambda t: (
                    "center",
                    760 - 20 * (t / chunk_duration),
                )
            )
            .with_start(chunk["start"])
            .with_duration(chunk_duration)
            .with_effects([
                vfx.FadeIn(0.2),
                vfx.FadeOut(0.2),
            ])
        )

        text_clips.append(subtitle)

    final = CompositeVideoClip(
        [background, headline] + text_clips,
        size=(1920, 1080),
    ).with_duration(duration)

    final = final.with_audio(audio)

    os.makedirs(GENERATED_VIDEOS_DIR, exist_ok=True)

    output_file = GENERATED_VIDEOS_DIR / f"{file_name}.mp4"

    final.write_videofile(
        str(output_file),
        fps=24,
        codec="libx264",
        audio_codec="aac",
    )

    return str(output_file)
