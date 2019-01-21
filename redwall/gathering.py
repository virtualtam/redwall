"""Gather images from Reddit"""
import logging
import os
from datetime import datetime
from urllib.parse import urlparse

import requests
from PIL import Image
from praw import Reddit
from requests.exceptions import HTTPError, TooManyRedirects
from sqlalchemy.orm.exc import NoResultFound

from .models import Submission, Subreddit


class Gatherer():
    """Gather information from Reddit and download submissions"""

    def __init__(self, config, db_session):
        """Load configuration and prepare resources"""
        self.reddit = Reddit(
            client_id=config.reddit_client_id,
            client_secret=config.reddit_client_secret,
            user_agent=config.reddit_user_agent,
        )

        self.data_dir = config.data_dir
        self.submission_limit = config.submission_limit
        self.subreddits = config.subreddits
        self.time_filter = config.time_filter

        self.db_session = db_session

    def download_top_submissions(self):
        """Get top submissions from the configured subreddits"""
        for subreddit in self.subreddits:
            try:
                db_subreddit = self.db_session.query(
                    Subreddit
                ).filter_by(name=subreddit).one()
            except NoResultFound:
                db_subreddit = Subreddit(name=subreddit)
                self.db_session.add(db_subreddit)
                self.db_session.commit()

            storage_dir = os.path.join(self.data_dir, subreddit)
            os.makedirs(storage_dir, exist_ok=True)

            for submission in self.get_subreddit_top_submissions(subreddit):
                if 'v.reddit' in submission.domain:
                    continue
                self.download_submission(storage_dir, db_subreddit, submission)

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

    def download_submission(self, storage_dir, db_subreddit, submission):
        """Save a submission's content along with its metadata"""
        # pylint: disable=too-many-locals
        logging.info("Saving %s", submission.id)

        parsed_url = urlparse(submission.url)
        filename = os.path.join(
            storage_dir,
            submission.id + '-' + os.path.basename(parsed_url.path)
        )

        # download the image linked to the submission
        if os.path.exists(filename):
            logging.warning("File exists, skipping download: %s", filename)
            image_downloaded = True
        else:
            try:
                download_submission_image(submission.url, filename)
                image_downloaded = True
            except (HTTPError, TooManyRedirects):
                image_downloaded = False

        # enrich metadata with the image's properties
        try:
            image = Image.open(filename)
            image_height_px = image.height
            image_width_px = image.width
        except (FileNotFoundError, OSError) as err:
            logging.error("Error reading %s: %s", filename, err)
            image_height_px = None
            image_width_px = None

        # prepare metadata
        try:
            author = submission.author.name
        except AttributeError:
            author = '[deleted]'

        created_utc = datetime.fromtimestamp(
            int(float(submission.created_utc))
        )

        # save metadata for future usage
        try:
            db_submission = self.db_session.query(
                Submission
            ).filter_by(post_id=submission.id).one()
        except NoResultFound:
            db_submission = Submission(
                subreddit_id=db_subreddit.id,
                post_id=submission.id,
                author=author,
                created_utc=created_utc,
                domain=submission.domain,
                over_18=submission.over_18,
                permalink=submission.permalink,
                score=submission.score,
                title=submission.title,
                url=submission.url,
                image_downloaded=image_downloaded,
                image_filename=filename,
                image_height_px=image_height_px,
                image_width_px=image_width_px,
            )
            self.db_session.add(db_submission)
            self.db_session.commit()


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

    except (HTTPError, TooManyRedirects) as err:
        logging.error(err)
        raise
