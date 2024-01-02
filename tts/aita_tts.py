import pyttsx3
import re
import os
import logging
from pathlib import Path
from time import sleep

logging.getLogger().setLevel(logging.INFO)

BASE = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
 <head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=768,height=1024"/>
  <link rel="stylesheet" href="../Styles/style.css" type="text/css"/>
  <title>Sonnet I</title>
 </head>
 <body>
  <div id="divTitle">
   <h1><span id="f001">I</span></h1>
  </div>
  <div id="divSonnet"> 
   <p>
__SPLIT-HERE__
   </p>
  </div>
 </body>
</html>"""

REPLACE_REGEX = r'(\d+F|\d+M|\d+f|\d+m|F\d+|M\d+|f\d+|m\d+)'

engine = pyttsx3.init()
engine.setProperty("voice", "mb-us2")
engine.setProperty("rate", 100)
engine.setProperty("pitch", 30)

def clean_line(line:str, replacement:dict={}) -> str:
    to_replace = re.findall(REPLACE_REGEX, line)
    for match in to_replace:
        replacement[match] = (match
            .replace('F', ' Female ')
            .replace('f', ' Female ')
            .replace('M', ' Male ')
            .replace('m', ' Male '))
        
    for k, v in replacement.items():
        line = line.replace(k, v)
    
    return re.sub(
        r'\s+',
        ' ',
        (line.replace('`', '\'')
            .replace('\u2019', '\'')
            .strip())
    )
        


def generate_media(data:dict, store_on_s3:bool=False, counter:int=1):
    
    base_start, base_end = BASE.split("__SPLIT-HERE__")
    base_key = f'audio/{data["subreddit"]}/{data["id"]}/'
    Path(base_key).mkdir(parents=True, exist_ok=True)

    subreddit = data["readable_subreddit"]
    stamp = data["readable_stamp"]

    sub_file = base_start
    dialog = f'Post on "{subreddit}" by "{data["author"]}", at "{stamp}"'
    sub_file+=f'\t<span id=f{counter:03}">'+dialog+'</span><br/>\n'
    counter+=1
    title = data["title"].replace('AITA', subreddit)
    lines = [title]+data["post_text"].split('.')
    for line in lines:
        line = clean_line(line)

        if not line:
            continue

        sub_file+=f'\t<span id=f{counter:03}">'+line+'</span><br/>\n'
        dialog+='\n'+line
        counter+=1

    audio_uri = base_key+"dialog.mp3"
    subs_uri = base_key+"subtitles.xhtml"
    engine.save_to_file(dialog, filename=audio_uri)
    engine.runAndWait()
    sub_file = sub_file.rsplit('<br/>', 1)[0]
    sub_file+=base_end

    with open(subs_uri, "w") as f:
        f.write(sub_file)

    timer = 1
    while ("dialog.mp3" not in os.listdir(base_key)):
        logging.warning("audio file not found. Retrying")
        sleep(timer)
        timer*2
        if timer>64:
            raise Exception("audio file not created")

    return {
        "post_id": data["id"],
        "subs_uri": subs_uri,
        "audio_uri": audio_uri
    }