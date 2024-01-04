import json
import os
import logging
from time import sleep

from pathlib import Path
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

logging.getLogger().setLevel(logging.INFO)

FONT = "Lane"
FONTSIZE = 30
COLOR = "white"
STROKE = "black"

def create_video(video_uri:str, audio_uri:str, subs_uri:str, post_id:str) -> None:
    Path("editor/output/").mkdir(parents=True, exist_ok=True)
    video_clip = VideoFileClip(video_uri)
    audio_clip = AudioFileClip(audio_uri)

    with open(subs_uri, "r") as f:
        data = json.loads(f.read())

    subtitles = [(v.get('text'), v.get('start'), v.get('end')) for v in data.values()]
    output = f"editor/output/{post_id}.mp4"

    text_clips = []
    for text, start_time, end_time in subtitles:
        text_clip = TextClip(
            text,
            fontsize=FONTSIZE,
            font=FONT,
            color=COLOR,
            size=video_clip.size,
            method="caption",
            stroke_color=STROKE,
            kerning=1
        )
        text_clip = text_clip.set_start(start_time).set_end(end_time)
        text_clips.append(text_clip)
    
    final_clip = CompositeVideoClip([video_clip]+text_clips)
    final_clip = final_clip.set_audio(audio_clip)
    final_clip.write_videofile(
        output,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp_audio.m4a",
        remove_temp=True
    )

    timer = 1
    while f"{post_id}.mp4" not in os.listdir("editor/output/"):
        sleep(timer)
        logging.warning(f"{post_id}.mp4 not present. Retrying")
        timer*=2
        if timer>64:
            raise Exception("Video was not created")
    
    return output