"""Configuration management"""
# pylint: disable=too-many-instance-attributes,too-few-public-methods
import logging
import os
from configparser import ConfigParser

DEFAULT_DATA_DIR = os.path.join(os.getcwd(), 'data')
DEFAULT_SUBMISSION_LIMIT = 20
DEFAULT_SUBREDDITS = [
    'EarthPorn',
    'NaturePics',
]
DEFAULT_TIME_FILTER = 'month'


class Config():
    """Configuration manager"""

    def __init__(self, config_files):
        """Load and verify configuration settings"""
        config = ConfigParser()
        config.read(config_files)

        try:
            self.reddit_client_id = config['reddit']['client_id']
            self.reddit_client_secret = config['reddit']['client_secret']
            self.reddit_user_agent = config['reddit']['user_agent']
        except KeyError as err:
            logging.warning("Reddit is not properly configured: %s", err)
            self.reddit_client_id = None
            self.reddit_client_secret = None
            self.reddit_client_agent = None

        try:
            self.data_dir = config['redwall'].get(
                'data_dir',
                DEFAULT_DATA_DIR
            )

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
            logging.warning(
                "Redwall is not configured, using default values: %s",
                err
            )
            self.data_dir = DEFAULT_DATA_DIR
            self.submission_limit = DEFAULT_SUBMISSION_LIMIT
            self.subreddits = DEFAULT_SUBREDDITS
            self.time_filter = DEFAULT_TIME_FILTER

        self.db_filename = os.path.join(self.data_dir, 'redwall.db')
