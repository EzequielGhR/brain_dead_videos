import json
import os
import logging
from time import sleep

from pathlib import Path
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

logging.getLogger().setLevel(logging.INFO)

#General settings for the videos
FONT = "Lane"
FONTSIZE = 20
COLOR = "white"
STROKE = "black"

def create_video(video_uri:str, audio_uri:str, subs_uri:str, post_id:str) -> str:
    """
    Creates the final video to be uploaded
    Params:
        video_uri: uri for source video cut from multimedia script.
        audio_uri: uri for audio source file from TTS script
        subs_uri: uri for subtitles source file from TTS script
        post_id: Id of the post from which the data is extracted.
    Output:
        The final video file path
    """
    #Creates output folder if it doesn't exist
    Path("editor/output/").mkdir(parents=True, exist_ok=True)
    video_clip = VideoFileClip(video_uri)
    audio_clip = AudioFileClip(audio_uri)

    #load subtitles file
    with open(subs_uri, "r") as f:
        data = json.loads(f.read())

    subtitles = [(v.get('text'), v.get('start'), v.get('end')) for v in data.values()]
    output = f"editor/output/{post_id}.mp4"

    #Create text clips with subtitles files
    text_clips = []
    for text, start_time, end_time in subtitles:
        text_clip = TextClip(
            text,
            fontsize=FONTSIZE,
            font=FONT,
            color=COLOR,
            size=video_clip.size,
            method="caption",
            #stroke_color=STROKE,
            kerning=1
        )
        text_clip = text_clip.set_start(start_time).set_end(end_time)
        text_clips.append(text_clip)
    
    #Create final composite using the source video cut and the text clips. Add the source audio to it.
    final_clip = CompositeVideoClip([video_clip]+text_clips)
    final_clip = final_clip.set_audio(audio_clip)
    final_clip.write_videofile(
        output,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp_audio.m4a",
        remove_temp=True
    )

    #wait for file to be created
    timer = 1
    while f"{post_id}.mp4" not in os.listdir("editor/output/"):
        sleep(timer)
        logging.warning(f"{post_id}.mp4 not present. Retrying")
        timer*=2
        if timer>64:
            raise Exception("Video was not created")
    
    return output