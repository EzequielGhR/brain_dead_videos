import requests
import logging
import argparse

from bs4 import BeautifulSoup
from datetime import datetime as dt
from .helper import *

logging.getLogger().setLevel(logging.INFO)

class AlreadyOnStorage(Exception): pass

def main_parser(post_id:str="", local:bool=False, force:bool=False) -> dict:
    url = get_post_url("AmItheAsshole", post_id)
    post_id = url.split("comments/")[-1].rsplit("/")[0]
    
    if (local and check_local_storage(post_id, "AmItheAsshole")) and (not force):
        raise AlreadyOnStorage(f"post {post_id} already on AmItheAsshole")

    logging.info("Making a request to: "+url)
    response = requests.get(url)
    if response.status_code != 200:
        logging.warning(f"Bad Request. Code: {response.status_code}, Msj: {response.text}")
        raise BadRequest(response.text)
    
    soup = BeautifulSoup(response.text, 'html.parser')

    logging.info(f"extracting general data for post {post_id}")
    title = soup.find("h1", id="post-title-t3_"+post_id)
    user = soup.find("span", slot="authorName")
    stamp = soup.find("faceplate-timeago")
    stamp = dt.strptime(
        parse_text(stamp.get('ts')),
        "%Y-%m-%dT%H:%M:%S.%f%z"
    )

    post_text = parse_text(soup.find("div", id=f"t3_{post_id}-post-rtjson-content").text)

    return {
        "title": parse_text(title.text),
        "author": parse_text(user.text),
        "timestamp": stamp,
        "readable_stamp": stamp.strftime("%d of %B %Y, at %H:%M"),
        "id": post_id,
        "post_url": url,
        "post_text": post_text,
        "subreddit": "AmItheAsshole",
        "readable_subreddit": "Am I the asshole"
    }