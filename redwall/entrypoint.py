"""Redwall - Console entrypoint"""
import logging
import os
from argparse import ArgumentParser
from configparser import ConfigParser

from .gathering import gather_subreddits


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

    config = ConfigParser()
    config.read([
        args.config,
        os.path.join(os.getcwd(), 'redwall.ini'),
        os.path.join(os.path.expanduser('~'), '.config', 'redwall.ini'),
        os.path.join(os.path.expanduser('~'), '.redwall'),
    ])

    gather_subreddits(config)
