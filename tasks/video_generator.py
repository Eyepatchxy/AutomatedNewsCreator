
from moviepy import *
from moviepy import AudioFileClip, VideoFileClip
import os
import math
from moviepy.video.fx import Loop
from tasks.paths import BACKGROUNDS_DIR, GENERATED_VIDEOS_DIR
from tasks.timeline_parser import build_timeline


def generate_video(file_name, chunks, audio_file, headline_text="BREAKING NEWS"):

    if isinstance(chunks, str):
        import json
        chunks = json.loads(chunks)

    audio = AudioFileClip(str(audio_file))
    duration = math.ceil(audio.duration)

    # Background (static or looped)
    background = VideoFileClip(str(BACKGROUNDS_DIR / "back.mp4"))
    background = background.with_effects([Loop(duration=duration)])

    timeline = build_timeline(file_name, chunks, duration)

    # Headline (static or long duration)
    headline = TextClip(
        text=headline_text,
        font_size=65,
        font="C:\\Users\\Acer\\AppData\\Local\\Microsoft\\Windows\\Fonts\\NotoSansDevanagari_Condensed-Bold.ttf",
        color="white",
        method="label",
        stroke_color="black",
        stroke_width=2
    ).with_position(("center", "top")) \
    .with_duration(duration)


    # Subtitles (dynamic, based on chunks)
    text_clips = []
    for chunk in timeline:
        text = TextClip(
            text=chunk["text"],
            font_size=50,
            font="C:\\Users\\Acer\\AppData\\Local\\Microsoft\\Windows\\Fonts\\NotoSansDevanagari_Condensed-Bold.ttf",   # ✅ IMPORTANT
            color='white',
            size=(background.w - 200, 300),
            method='caption',
            stroke_color='black',      # improves readability
            stroke_width=2
        ).with_position(("center", "bottom")) \
        .with_start(chunk["start"]) \
        .with_duration(chunk["end"] - chunk["start"])
        
        text_clips.append(text)

    final = CompositeVideoClip([background, headline] + text_clips)

    final = final.with_audio(audio)

    os.makedirs(GENERATED_VIDEOS_DIR, exist_ok=True)
    output_file = GENERATED_VIDEOS_DIR / f"{file_name}.mp4"
    final.write_videofile(
        str(output_file),
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )
    return str(output_file)
    
