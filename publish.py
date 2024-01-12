from db.engine import DB
from argparse import ArgumentParser
from editor.aita_editor import create_video as aita_video

#initialize db instance
db = DB()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--post-id", type=str)
    
    args = parser.parse_args()
    
    post_id = args.post_id
    
    #get multimedia data
    if post_id:
        data = db.get_multimedia_by_post_id(post_id)
    else:
        data = db.get_multimedia_record(by="created_at")
    
    video_uri = data["video_uri"]
    audio_uri = data["audio_uri"]
    subs_uri = data["subs_uri"]
    post_id = data["post_id"] #in case is not provided as a script param

    #create final video
    aita_video(video_uri, audio_uri, subs_uri, post_id)