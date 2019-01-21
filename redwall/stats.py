"""Statistics about local data"""
from sqlalchemy import func

from .models import Subreddit


def display_stats(db_session):
    """Print statistics about collected submissions"""
    res = db_session.query(Subreddit).order_by(func.lower(Subreddit.name)).all()
    for subreddit in res:
        print("{:>5}  {}".format(len(subreddit.submissions), subreddit.name))
