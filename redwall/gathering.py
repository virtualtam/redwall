"""Gather images from Reddit"""
import json
import logging
import os
from urllib.parse import urlparse

import requests
from PIL import Image
from praw import Reddit

DEFAULT_DATA_DIR = os.path.join(os.getcwd(), 'data')
DEFAULT_SUBMISSION_LIMIT = 20
DEFAULT_SUBREDDITS = [
    'EarthPorn',
    'NaturePics',
]
DEFAULT_TIME_FILTER = 'month'


class Gatherer():
    """Gather information from Reddit and download submissions"""

    def __init__(self, config):
        """Load configuration and prepare resources"""
        self.config = config

        self.reddit = Reddit(
            client_id=config['reddit']['client_id'],
            client_secret=config['reddit']['client_secret'],
            user_agent=config['reddit']['user_agent'],
        )

        self.data_dir = DEFAULT_DATA_DIR
        self.submission_limit = DEFAULT_SUBMISSION_LIMIT
        self.subreddits = DEFAULT_SUBREDDITS
        self.time_filter = DEFAULT_TIME_FILTER

        try:
            self.submission_limit = config['redwall'].get(
                'submission_limit',
                DEFAULT_SUBMISSION_LIMIT
            )
            self.submission_limit = int(self.submission_limit)

            self.time_filter = config['redwall'].get(
                'time_filter',
                DEFAULT_TIME_FILTER
            )

            self.subreddits = config['redwall']['subreddits']
            self.subreddits = self.subreddits.strip().replace(',', ' ').split()

        except KeyError as err:
            logging.warning("Missing configuration: %s", err)

    def download_top_submissions(self):
        """Get top submissions from the configured subreddits"""
        for subreddit in self.subreddits:
            storage_dir = os.path.join(self.data_dir, subreddit)
            os.makedirs(storage_dir, exist_ok=True)

            for submission in self.get_subreddit_top_submissions(subreddit):
                if 'v.reddit' in submission.domain:
                    continue
                self.download_submission(storage_dir, submission)

    def get_subreddit_top_submissions(self, subreddit):
        """Get top submissions from a subreddit"""
        logging.info(
            "Gathering the top %d submissions from /r/%s for this %s",
            self.submission_limit,
            subreddit,
            self.time_filter,
        )

        return self.reddit.subreddit(subreddit).top(
            limit=self.submission_limit,
            time_filter=self.time_filter,
        )

    @staticmethod
    def download_submission(storage_dir, submission):
        """Save a submission's content along with its metadata"""
        logging.info("Saving %s", submission.id)

        submission_dir = os.path.join(storage_dir, submission.id)
        os.makedirs(submission_dir, exist_ok=True)

        parsed_url = urlparse(submission.url)
        filename = os.path.join(
            submission_dir,
            os.path.basename(parsed_url.path)
        )

        # prepare metadata
        metadata = {
            'id': submission.id,
            'created_utc': submission.created_utc,
            'domain': submission.domain,
            'image_filename': filename,
            'over_18': submission.over_18,
            'permalink': submission.permalink,
            'score': submission.score,
            'title': submission.title,
            'url': submission.url,
        }
        try:
            metadata['author'] = submission.author.name
        except AttributeError:
            metadata['author'] = '[deleted]'

        # download the image linked to the submission
        if os.path.exists(filename):
            logging.warning("File exists, skipping download: %s", filename)
        else:
            download_submission_image(submission.url, filename)

        # enrich metadata with the image's properties
        try:
            image = Image.open(filename)
            metadata['image_height'] = image.height
            metadata['image_width'] = image.width
        except (FileNotFoundError, OSError) as err:
            logging.error("Error reading %s: %s", filename, err)

        # save metadata for future usage
        with open(os.path.join(submission_dir, 'meta.json'), 'w') as f_meta:
            f_meta.write(json.dumps(metadata, sort_keys=True, indent=2))


def download_submission_image(submission_url, filename):
    """Download the image linked to a submission"""
    logging.info("Downloading %s", submission_url)

    headers = {
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            + ' (KHTML, like Gecko) Chrome/56.0.2924.87'
            + ' Safari/537.36',
        'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,'
            + 'image/webp,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
    }

    try:
        response = requests.get(submission_url, headers=headers)
        response.raise_for_status()

        with open(os.path.join(filename), 'wb') as f_img:
            f_img.write(response.content)

    except requests.exceptions.TooManyRedirects as err:
        logging.error(err)
