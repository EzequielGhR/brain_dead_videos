from db.engine import DB
from argparse import ArgumentParser
from editor.aita_editor import create_video as aita_video

db = DB()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--post-id", type=str)
    
    args = parser.parse_args()
    
    post_id = args.post_id
    
    if post_id:
        data = db.get_multimedia_by_post_id(post_id)
    else:
        data = db.get_multimedia_record(by="created_at")
    
    print(data)
    
    video_uri = data["video_uri"]
    audio_uri = data["audio_uri"]
    subs_uri = data["subs_uri"]
    post_id = data["post_id"] #in case is not provided as a script param

    aita_video(video_uri, audio_uri, subs_uri, post_id)