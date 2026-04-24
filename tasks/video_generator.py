
from moviepy import *
from moviepy import AudioFileClip, VideoFileClip
import os
import math
from moviepy.video.fx import Loop
from moviepy.video.fx import Resize
from moviepy.video.fx import Crop
from tasks.timeline_parser import build_timeline


def generate_video(file_name, chunks, audio_file):

    audio = AudioFileClip("{audio_file}.wav")
    duration = math.ceil(audio.duration)

    # Background (static or looped)
    background = VideoFileClip("back.mp4")
    background = background.loop(duration=duration)  

    timeline = build_timeline(file_name, chunks, duration)

    # Headline (static or long duration)
    headline = TextClip(
        text="BREAKING NEWS",
        font_size=70,
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
            font_size=60,
            font="C:\\Users\\Acer\\AppData\\Local\\Microsoft\\Windows\\Fonts\\NotoSansDevanagari_Condensed-Bold.ttf",   # ✅ IMPORTANT
            color='white',
            size=(background.w - 200, None),
            method='caption',
            stroke_color='black',      # improves readability
            stroke_width=2
        ).with_position(("center", "bottom")) \
        .with_start(chunk["start"]) \
        .with_duration(chunk["end"] - chunk["start"])
        
        text_clips.append(text)

    final = CompositeVideoClip([background, headline] + text_clips)

    final = final.with_audio(audio)

    final.write_videofile(f"{file_name}.mp4", fps=24)

    return f"{file_name}.mp4"
    
    