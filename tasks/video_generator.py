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
from paths import PROJECT_ROOT, GENERATED_BACKIMAGES_DIR, GENERATED_VIDEOS_DIR, HORIZONTAL_LAYOUT_FILE, VERTICAL_LAYOUT_FILE, FONT_FILE
from tasks.timeline_parser import build_timeline
from gui.components.progress_pipeline import ProgressPipeline
from gui.utils.RenderLogger import RenderLogger
from gui.state.models import VideoType

load_dotenv(PROJECT_ROOT / ".env")

DURATION_PER_IMAGE = 30

LAYOUT_SPECS = {
    VideoType.FULL: {
        "canvas_size": (1920, 1080),
        "layout_file": HORIZONTAL_LAYOUT_FILE,
        "caption": {
            "font_size": 42,
            "size": (1275, 120),
            "position": (445, 820),
            "text_align": "left",
            "horizontal_align": "left",
            "interline": 4,
        },
    },
    VideoType.SHORT: {
        "canvas_size": (1080, 1920),
        "layout_file": VERTICAL_LAYOUT_FILE,
        "caption": {
            "font_size": 44,
            "size": (600, 260),
            "position": (380, 1580),
            "text_align": "left",
            "horizontal_align": "left",
            "interline": 12,
        },
    },
}


def normalize_video_type(video_type) -> VideoType:
    if isinstance(video_type, VideoType):
        return video_type

    try:
        return VideoType(video_type)
    except ValueError:
        return VideoType.FULL


def create_background(file_name, duration, layout_spec):

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
            .resized(layout_spec["canvas_size"])
            .resized(lambda t: 1.08 + 0.02 * t)

        )

        clips.append(clip)

    return concatenate_videoclips(clips, method="compose").with_duration(duration)


def generate_video(
    file_name,
    chunks,
    audio_file,
    pipeline: ProgressPipeline | str | None = None,
    headline_text="BREAKING NEWS",
    video_type: VideoType = VideoType.FULL,
):
    if isinstance(pipeline, str):
        headline_text = pipeline
        pipeline = None

    if pipeline is not None:
        pipeline.start_stage(8)

    if isinstance(chunks, str):
        chunks = json.loads(chunks)

    audio = AudioFileClip(str(audio_file))
    duration = math.ceil(audio.duration)
    video_type = normalize_video_type(video_type)
    layout_spec = LAYOUT_SPECS[video_type]

    background = create_background(file_name, duration, layout_spec)

    timeline = build_timeline(file_name, chunks, duration)

    # headline = (
    #     TextClip(
    #         text=headline_text,
    #         font_size=65,
    #         font=FONT_PATH,
    #         color="white",
    #         method="caption",
    #         size=(1800, 180),
    #         stroke_color="black",
    #         stroke_width=2,
    #         text_align="center",
    #     )
    #     .with_position(("center", 10))
    #     .with_duration(duration)
    # )

    layout_overlay = (
        ImageClip(str(layout_spec["layout_file"]))
        .with_duration(duration)
        .resized(layout_spec["canvas_size"])
    )

    text_clips = []
    caption_spec = layout_spec["caption"]

    for chunk in timeline:
        chunk_duration = chunk["end"] - chunk["start"]
        if chunk_duration <= 0:
            continue

        subtitle = (
            TextClip(
                text=chunk["text"],
                font_size=caption_spec["font_size"],
                font=FONT_FILE,
                color="black",
                size=caption_spec["size"],
                method="caption",
                text_align=caption_spec["text_align"],
                horizontal_align=caption_spec["horizontal_align"],
                interline=caption_spec["interline"]
            )   
            .with_position(caption_spec["position"])
            .with_start(chunk["start"])
            .with_duration(chunk_duration)
            .with_effects([
                vfx.FadeIn(0.2),
                vfx.FadeOut(0.2),
            ])
        )

        text_clips.append(subtitle)

    final = CompositeVideoClip(
        [
            background,
            layout_overlay,
            *text_clips,
        ],
        size=layout_spec["canvas_size"],
    ).with_duration(duration)

    final = final.with_audio(audio)

    os.makedirs(GENERATED_VIDEOS_DIR, exist_ok=True)

    output_file = GENERATED_VIDEOS_DIR / f"{file_name}.mp4"

    logger = RenderLogger(pipeline) if pipeline is not None else None

    final.write_videofile(
        str(output_file),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        logger=logger
    )

    if pipeline is not None:
        pipeline.complete_stage(8)

    return str(output_file)
