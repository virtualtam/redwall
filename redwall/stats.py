"""Statistics about local data"""
from sqlalchemy import func

from .models import Submission, Subreddit


def display_stats(db_session):
    """Print statistics about collected submissions"""
    res = db_session.query(Subreddit, func.count(Submission.id))\
        .join(Submission)\
        .group_by(Subreddit.id)\
        .order_by(func.lower(Subreddit.name))

    grand_total = 0

    for subreddit, submission_total in res:
        grand_total += int(submission_total)
        print("{:>5}  {}".format(submission_total, subreddit.name))

    print("\n{:>5}  TOTAL".format(grand_total))
