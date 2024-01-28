import logging
import os

from argparse import ArgumentParser
from random import randint, choice
from pathlib import Path
from moviepy.editor import VideoFileClip
from mutagen.mp3 import MP3
from db.engine import DB
from tts.aita_tts import generate_media as aita_media

#Set source videofile location
SOURCE = f"sources/{choice(os.listdir('sources'))}"

db = DB()

def create_cut(length:float, out_path:str) -> str:
    """
    Creates a video cut of the original source of a given length.
    Params:
        length: Length of the final ccut in seconds.
        out_path: output location for the video cut.
    Output:
        video cut path.
    """
    #Create output folders if they don't exist
    Path(out_path).mkdir(parents=True, exist_ok=True)
    #Create cut from source starting at a random point accounting for final length
    video = VideoFileClip(SOURCE)
    start = randint(10, int(video.end-length-2))
    end = start+int(length)+1
    out = video.subclip(start, end)
    #Define output file path  and write video file
    video_uri = f"{out_path}/video_cut.mp4"
    logging.info("saving video to: "+video_uri)
    out.write_videofile(video_uri)
    return video_uri
    

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--post-id", type=str)
    
    args = parser.parse_args()

    post_id = args.post_id

    #Fetch post record by post id or latest by reddit timestamp from the db
    record = db.get_post_record(id=post_id)
    #Create general media data
    multimedia_data = aita_media(record)
    audio_uri = multimedia_data["audio_uri"]

    #Create video cut with lenght of the audio file created
    length = MP3(audio_uri).info.length
    out_path = audio_uri.rsplit('/', 1)[0].replace("audio", "video")
    logging.info(f"Creating cut of length: "+str(length))
    video_uri = create_cut(length, out_path)

    #Complete data and add it to multimedia table
    multimedia_data["video_uri"] = video_uri
    db.add_multimedia_data(multimedia_data)
