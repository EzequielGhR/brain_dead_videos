from argparse import ArgumentParser
from db.engine import DB
from tts.aita_tts import generate_media as aita_media

db = DB()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--post-id", type=str)
    
    args = parser.parse_args()

    post_id = args.post_id

    record = db.get_post_record(id=post_id)
    multimedia_data = aita_media(record)
    db.add_multimedia_data(multimedia_data)
