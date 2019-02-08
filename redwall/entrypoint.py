"""Redwall - Console entrypoint"""
import logging
import os
import time
from argparse import ArgumentParser

from screeninfo import get_monitors
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from .config import Config
from .election import Chooser
from .gathering import Gatherer
from .models import Base, History
from .stats import display_stats


def main():
    """Main entrypoint"""
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format='%(asctime)s %(levelname)-7s %(message)s')
    logging.Formatter.converter = time.gmtime

    parser = ArgumentParser(
        description="Redwall helps you manage a collection of curated \
        wallpapers, courtesy of the Reddit community.",
        epilog="~ The front wallpaper of your computer ~",
    )

    parser.add_argument(
        '-c',
        '--config',
        default='',
        help="Configuration file"
    )

    subparsers = parser.add_subparsers(
        dest='command',
        help="Command to run",
    )
    subparsers.add_parser(
        'current',
        help="Display information about the currently selected entry"
    )
    subparsers.add_parser('gather', help="Gather submission media from Reddit")
    subparsers.add_parser(
        'history',
        help="Display the history of selected entries",
    )
    subparsers.add_parser(
        'list-candidates',
        help="List submissions suitable for the current monitor setup",
    )
    subparsers.add_parser(
        'random',
        help="Select a random submission suitable for the current monitor \
            setup and print its path",
    )
    subparsers.add_parser(
        'stats',
        help="Display statistics about gathered submissions"
    )

    args = parser.parse_args()

    config = Config([
        args.config,
        os.path.join(os.getcwd(), 'redwall.ini'),
        os.path.join(os.path.expanduser('~'), '.config', 'redwall.ini'),
        os.path.join(os.path.expanduser('~'), '.redwall'),
    ])

    os.makedirs(config.data_dir, exist_ok=True)
    engine = create_engine('sqlite:///%s' % config.db_filename)

    try:
        Base.metadata.create_all(engine)
    except OperationalError as err:
        logging.error(
            "Error opening database '%s': %s",
            config.db_filename,
            err
        )
        exit(1)

    db_session = sessionmaker(bind=engine)()

    if args.command == 'current':
        entry = db_session.query(
            History
        ).order_by(History.id.desc()).first()
        if entry:
            print("%s | %s" % (entry.date, entry.submission.pprint()))
        else:
            print("Nothing found!")

    elif args.command == 'gather':
        gatherer = Gatherer(config, db_session)
        gatherer.download_top_submissions()

    elif args.command == 'history':
        entries = db_session.query(
            History
        ).order_by(History.id.asc()).all()

        for entry in entries:
            print("%s | %s" % (entry.date, entry.submission.pprint()))

    elif args.command == 'list-candidates':
        chooser = Chooser(db_session, get_monitors())
        chooser.list_candidates_by_subreddit()

    elif args.command == 'random':
        chooser = Chooser(db_session, get_monitors())
        submission = chooser.get_random_candidate()
        print(submission.image_filename)

    elif args.command == 'stats':
        display_stats(db_session)

    else:
        logging.warning("Unknown command: %s", args.command)
