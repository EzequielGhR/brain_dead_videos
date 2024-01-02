import logging

from argparse import ArgumentParser
from db.engine import DB
from scrapper.aita_scrapper import main_parser as aita_parser

logging.getLogger().setLevel(logging.INFO)

db = DB()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--post-id", type=str)
    parser.add_argument("--local", type=str)
    parser.add_argument("--force", type=str)

    args = parser.parse_args()

    post_id = args.post_id
    local = eval(args.local.lower().capitalize()) if args.local else False
    force = eval(args.force.lower().capitalize()) if args.force else False

    data = aita_parser(post_id, local, force)
    db.add_post_data(data)