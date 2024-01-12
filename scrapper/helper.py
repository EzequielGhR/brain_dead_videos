import requests
import logging
import os
import json

from bs4 import BeautifulSoup
from pathlib import Path

class BadRequest(Exception): pass

def parse_text(text:str) -> str:
    """
    Cleanes a string of text line by line
    """
    logging.info("parsing text")
    lines = text.split('\n')
    stripped = [line.strip() for line in lines if line.strip()]
    return '\n'.join(stripped)

def get_post_url(subr:str, post_id:str="") -> str:
    """
    If post_id is provided it will fetch the url for that post.
    Otherwise it will return the last main page post
    """
    #preset url and tail string for eval
    url = f"https://www.reddit.com/r/{subr}/"
    tail_str = "middle_soup.find_all(\"a\", attrs={\"slot\": \"full-post-link\"})[2].get(\"href\")"

    if post_id:
        url += f"comments/{post_id}/"
        tail_str = "middle_soup.find(\"shreddit-redirect\").get(\"href\")"

    logging.info("making a request to: "+url)    
    response = requests.get(url)
    if response.status_code != 200:
        logging.warning(f"Bad Request. Code: {response.status_code}, Msj: {response.text}")
        raise BadRequest(response.text)
    
    #get data and create full url
    middle_soup = BeautifulSoup(response.text, 'html.parser')
    return "https://www.reddit.com"+eval(tail_str)

def check_local_storage(post_id:str, subr:str) -> bool:
    """
    Checks for local json storage
    """
    Path(f"../storage/{subr}").mkdir(parents=True, exist_ok=True)
    if f"{post_id}.json" in os.listdir(f"../storage/{subr}/"):
        logging.info("post already exists")
        return True
    return False

def save_local_json(json_:dict, force:bool=False):
    subr = json_["subReddit"]
    id_ = json_["postId"]
    if force:
        logging.warning("Forcing overwrite of data")
    elif check_local_storage(post_id=id_, subr=subr):
        return id_
    
    with open(f"../storage/{subr}/{id_}.json", "w") as f:
        f.write(json.dumps(json_, indent=4, sort_keys=True))
        
    return id_