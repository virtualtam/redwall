"""Find images to set as wallpapers for the current monitor configuration"""
import random

from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from .models import History, Submission, Subreddit


class Chooser():
    """Choose submissions suitable for wallpaper usage"""

    def __init__(self, db_session, monitors):
        """Load configuration and prepare resources"""
        self.db_session = db_session

        # when choosing the same image for all monitors, it should be:
        # - wider than the widest monitor
        # - taller than the tallest monitor
        self.image_height = max([m.height for m in monitors])
        self.image_width = max([m.width for m in monitors])

    def get_candidates(self):
        """Get suitable submissions for the current monitor setup"""
        return self.db_session.query(Submission).filter(
            Submission.image_height_px >= self.image_height,
            Submission.image_width_px >= self.image_width,
        ).all()

    def get_random_candidate(self):
        """Choose a random submission among suitable candidates"""
        submissions = self.get_candidates()
        submission = random.choice(submissions)

        try:
            historow = self.db_session.query(
                History
            ).filter_by(submission_id=submission.id).one()
        except NoResultFound:
            historow = History(submission_id=submission.id)
            self.db_session.add(historow)
            self.db_session.commit()

        return submission

    def list_candidates_by_subreddit(self):
        """Pretty-print suitable submissions"""
        subreddits = self.db_session.query(
            Subreddit
        ).order_by(func.lower(Subreddit.name)).all()

        for subreddit in subreddits:
            print("\n/r/%s" % subreddit.name)
            print("---%s" % (len(subreddit.name) * "-"))
            submissions = self.db_session.query(
                Submission
            ).filter(
                Submission.subreddit_id == subreddit.id,
                Submission.image_height_px >= self.image_height,
                Submission.image_width_px >= self.image_width,
            ).order_by(Submission.created_utc).all()

            for submission in submissions:
                print(submission.pprint())
