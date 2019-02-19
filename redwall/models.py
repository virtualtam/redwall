"""Models"""
# pylint: disable=invalid-name,too-few-public-methods
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Subreddit(Base):
    """Subreddit representation"""

    __tablename__ = 'subreddits'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    submissions = relationship('Submission', back_populates='subreddit')

    def __repr__(self):
        return "<Subreddit(name='%s')>" % (self.name)


class Submission(Base):
    """Reddit submission representation"""

    __tablename__ = 'submissions'

    id = Column(Integer, primary_key=True)

    subreddit_id = Column(Integer, ForeignKey('subreddits.id'))
    subreddit = relationship('Subreddit', back_populates='submissions')

    post_id = Column(String)

    author = Column(String)
    created_utc = Column(DateTime)
    domain = Column(String)
    over_18 = Column(Boolean)
    permalink = Column(String)
    score = Column(Integer)
    title = Column(String)
    url = Column(String)

    image_downloaded = Column(Boolean)
    image_filename = Column(String)
    image_height_px = Column(Integer)
    image_width_px = Column(Integer)

    def __repr__(self):
        return "<Submission(subreddit='%s', id='%s', title='%s')>" % (
            self.subreddit.name,
            self.post_id,
            self.title,
        )

    @property
    def post_url(self):
        """URL of the original Reddit post"""
        return "https://reddit.com/r/%s/comments/%s/" % (
            self.subreddit.name,
            self.post_id
        )

    def brief(self):
        """Brief string representation"""
        try:
            return "%s | %d x %d | %s" % (
                self.post_id,
                int(self.image_width_px),
                int(self.image_height_px),
                self.title
            )
        except TypeError:
            return "%s |    N/A     | %s" % (
                self.post_id,
                self.title
            )

    def pprint(self):
        """Pretty-printable string representation"""
        try:
            return (
                "Title        %s\n"
                "Author       u/%s\n"
                "Date         %s\n"
                "Post URL     %s\n"
                "Image URL    %s\n"
                "Image size   %d x %d\n"
                "Filename     %s"
            ) % (
                self.title,
                self.author,
                self.created_utc,
                self.post_url,
                self.url,
                int(self.image_width_px),
                int(self.image_height_px),
                self.image_filename,
            )
        except TypeError:
            return (
                "Title        %s\n"
                "Author       u/%s\n"
                "Date         %s\n"
                "Post URL     %s\n"
                "Image URL    %s\n"
                "Image size   N/A\n"
                "Filename     %s"
            ) % (
                self.title,
                self.author,
                self.created_utc,
                self.post_url,
                self.url,
                self.image_filename,
            )


class History(Base):
    """History tracks wallpaper selections"""

    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey('submissions.id'))
    submission = relationship('Submission')
    date = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return "<History(id='%s', title='%s')>" % (
            self.submission.post_id,
            self.submission.title,
        )
