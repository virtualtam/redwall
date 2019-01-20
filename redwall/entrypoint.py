"""Redwall - Console entrypoint"""
import logging
import os
from argparse import ArgumentParser

from .config import Config
from .gathering import Gatherer


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

    args = parser.parse_args()

    config = Config([
        args.config,
        os.path.join(os.getcwd(), 'redwall.ini'),
        os.path.join(os.path.expanduser('~'), '.config', 'redwall.ini'),
        os.path.join(os.path.expanduser('~'), '.redwall'),
    ])

    gatherer = Gatherer(config)
    gatherer.download_top_submissions()
