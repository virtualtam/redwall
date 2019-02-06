"""Redwall - Console entrypoint"""
import logging
import os
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

    parser = ArgumentParser()
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
    subparsers.add_parser('current')
    subparsers.add_parser('gather')
    subparsers.add_parser('history')
    subparsers.add_parser('random')
    subparsers.add_parser('stats')

    args = parser.parse_args()

    config = Config([
        args.config,
        os.path.join(os.getcwd(), 'redwall.ini'),
        os.path.join(os.path.expanduser('~'), '.config', 'redwall.ini'),
        os.path.join(os.path.expanduser('~'), '.redwall'),
    ])

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
        print("%s | %s" % (entry.date, entry.submission.pprint()))

    elif args.command == 'gather':
        gatherer = Gatherer(config, db_session)
        gatherer.download_top_submissions()

    elif args.command == 'history':
        entries = db_session.query(
            History
        ).order_by(History.id.asc()).all()

        for entry in entries:
            print("%s | %s" % (entry.date, entry.submission.pprint()))

    elif args.command == 'random':
        # when choosing the same image for all monitors, it should be:
        # - wider than the widest monitor
        # - taller than the tallest monitor
        monitors = get_monitors()
        height = max([m.height for m in monitors])
        width = max([m.width for m in monitors])

        chooser = Chooser(db_session, height, width)
        submission = chooser.get_random_candidate()

        print(submission.image_filename)

    elif args.command == 'stats':
        display_stats(db_session)

    else:
        logging.warning("Unknown command: %s", args.command)
