"""Models"""
# pylint: disable=invalid-name,too-few-public-methods
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
