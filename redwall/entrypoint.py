"""Redwall - Console entrypoint"""
import logging
import os

import praw

from .gathering import get_subreddit_top_submissions

SUBREDDITS = [
    'AerialPorn',
    'CityPorn',
    'EarthPorn',
    'InfrastructurePorn',
    'NaturePics',
    'SkyPorn',
    'SpacePorn',
    'wallpaper',
    'WaterPorn',
]

DATA_DIR = os.path.join(os.path.abspath(os.curdir), 'data')

LIMIT = 20
TIME_FILTER = 'month'

PRAW_PROFILE = 'vt'


def main():
    """Main entrypoint"""
    logging.getLogger().setLevel(logging.INFO)

    reddit = praw.Reddit(PRAW_PROFILE)

    for subreddit in SUBREDDITS:
        get_subreddit_top_submissions(reddit, subreddit, TIME_FILTER, LIMIT,
                                      DATA_DIR)
