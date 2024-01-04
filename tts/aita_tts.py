import pyttsx3
import re
import os
import json
import logging

from pathlib import Path
from time import sleep
from mutagen.mp3 import MP3
from pydub import AudioSegment

logging.getLogger().setLevel(logging.INFO)

REPLACE_REGEX = r'(\d+F|\d+M|\d+f|\d+m|F\d+|M\d+|f\d+|m\d+)'

engine = pyttsx3.init()
engine.setProperty("voice", "mb-us2")
engine.setProperty("rate", 100)
engine.setProperty("pitch", 30)

def clean_line(line:str, replacement:dict={}) -> str:
    to_replace = re.findall(REPLACE_REGEX, line)
    for match in to_replace:
        replacement[match] = (match
            .replace('M', ' Male ')
            .replace('m', ' Male ')
            .replace('F', ' Female ')
            .replace('f', ' Female '))
        
    for k, v in replacement.items():
        line = line.replace(k, v)
    
    line = re.sub(
        r'\s+',
        ' ',
        (line.replace('`', '\'')
            .replace('\u2019', '\'')
            .replace("\u201c", "\"")
            .replace("\u201d", "\"")
            .strip())
    )

    return re.sub(
        r'^AITA|^Aita',
        "Am I the asshole",
        line.replace(" aita", " am I the asshole")
    )

def process_audio_and_subs(audio_uri:str, subtitles:dict, start:float=0):
    audio_segments = []
    for i in range(len(subtitles.keys())):
        audio = audio_uri+subtitles[i+1]["line"]+".mp3"
        length = MP3(audio).info.length
        end = start+length-0.075 #estimate
        subtitles[i+1]["start"] = round(start, 2)
        subtitles[i+1]["end"] = round(end, 2)
        start = end
        audio_segments.append(AudioSegment.from_mp3(audio))

    with open(audio_uri+"subtitles.json", "w") as f:
        f.write(json.dumps(subtitles, indent=4))
    
    concatenated_audio = sum(audio_segments)
    concatenated_audio.export(audio_uri+"dialog.mp3", format="mp3")

    for file_ in os.listdir(audio_uri):
        if file_ in ("dialog.mp3", "subtitles.json"):
            continue
        os.remove(audio_uri+file_)
    
    return audio_uri+"dialog.mp3", audio_uri+"subtitles.json"

def generate_media(data:dict, store_on_s3:bool=False, counter:int=1):
    
    audio_uri = f'audio/{data["subreddit"]}/{data["id"]}/'
    Path(audio_uri).mkdir(parents=True, exist_ok=True)

    subreddit = data["readable_subreddit"]
    stamp = data["readable_stamp"]

    sub_file = {}
    dialog = f'Post on "{subreddit}" by "{data["author"]}", at "{stamp}"'
    engine.save_to_file(dialog, filename=audio_uri+f"line_{counter:03}.mp3")
    sub_file[counter] = {"line": f"line_{counter:03}", "text": dialog}
    counter+=1
    title = data["title"].replace('AITA', subreddit)
    lines = [title]+data["post_text"].split('.')
    for line in lines:
        line = clean_line(line)

        if not line:
            continue

        sub_file[counter] = {"line": f"line_{counter:03}", "text": line}
        engine.save_to_file(line, filename=audio_uri+f"line_{counter:03}.mp3")
        counter+=1
    engine.runAndWait()

    timer = 1
    while ((file_:=f"line_{(counter-1):03}.mp3") not in os.listdir(audio_uri)):
        logging.warning(f"{file_} file not found in {audio_uri}. Retrying")
        sleep(timer)
        timer*=2
        if timer>64:
            raise Exception("audio file not created")
    
    audio_uri, subs_uri = process_audio_and_subs(audio_uri, sub_file)

    return {
        "post_id": data["id"],
        "subs_uri": subs_uri,
        "audio_uri": audio_uri
    }