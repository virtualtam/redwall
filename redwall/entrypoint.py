"""Redwall - Console entrypoint"""
import logging
import os
from argparse import ArgumentParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import Config
from .gathering import Gatherer
from .models import Base
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
    subparsers.add_parser('gather')
    subparsers.add_parser('stats')

    args = parser.parse_args()

    config = Config([
        args.config,
        os.path.join(os.getcwd(), 'redwall.ini'),
        os.path.join(os.path.expanduser('~'), '.config', 'redwall.ini'),
        os.path.join(os.path.expanduser('~'), '.redwall'),
    ])

    engine = create_engine('sqlite:///%s' % config.db_filename)
    Base.metadata.create_all(engine)
    db_session = sessionmaker(bind=engine)()

    if args.command == 'gather':
        gatherer = Gatherer(config, db_session)
        gatherer.download_top_submissions()
    elif args.command == 'stats':
        display_stats(db_session)
    else:
        logging.warning("Unknown command: %s", args.command)
