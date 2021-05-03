"""Redwall - Console entrypoint"""
import logging
import os
import sys
import time

import click
from screeninfo import get_monitors
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from .config import Config
from .election import Chooser
from .gathering import Gatherer
from .models import Base, History, Submission
from .stats import display_stats


@click.group()
@click.option(
    "-c", "--config-path", type=click.Path(exists=True), help="Configuration file"
)
@click.help_option("-h", "--help")
@click.version_option()
@click.pass_context
def redwall(ctx, config_path):
    """Redwall, the front wallpaper to your monitor(s)

    Redwall helps you manage a collection of curated wallpapers,
    courtesy of the Reddit community.
    """
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format="%(asctime)s %(levelname)-7s %(message)s")
    logging.Formatter.converter = time.gmtime

    config = Config(
        [
            config_path if config_path else "",
            os.path.join(os.getcwd(), "redwall.ini"),
            os.path.join(os.path.expanduser("~"), ".config", "redwall.ini"),
            os.path.join(os.path.expanduser("~"), ".redwall"),
        ]
    )

    os.makedirs(config.data_dir, exist_ok=True)
    engine = create_engine("sqlite:///%s" % config.db_filename)

    try:
        Base.metadata.create_all(engine)
    except OperationalError as err:
        logging.error("Error opening database '%s': %s", config.db_filename, err)
        sys.exit(1)

    db_session = sessionmaker(bind=engine)()

    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["db_session"] = db_session


@redwall.command()
@click.option(
    "-f",
    "--filename",
    is_flag=True,
    help="Only print the local filename",
)
@click.pass_context
def current(ctx, filename: bool):
    """Display information about the currently selected entry"""
    entry = ctx.obj["db_session"].query(History).order_by(History.id.desc()).first()

    if not entry:
        print("Nothing found!")
    elif filename:
        print(entry.submission.image_filename)
    else:
        print("Current image, selected on %s\n" % entry.date)
        print(entry.submission.pprint())


@redwall.command()
@click.pass_context
def gather(ctx):
    """Gather submission media from Reddit"""
    gatherer = Gatherer(ctx.obj["config"], ctx.obj["db_session"])
    gatherer.download_top_submissions()


@redwall.command()
@click.pass_context
def history(ctx):
    """Display the history of selected entries"""
    entries = ctx.obj["db_session"].query(History).order_by(History.id.asc()).all()

    for entry in entries:
        print("%s | %s" % (entry.date, entry.submission.brief()))


@redwall.command()
@click.option(
    "-f",
    "--filename",
    is_flag=True,
    help="Only print the local filename",
)
@click.argument("post_id")
@click.pass_context
def info(ctx, post_id, filename: bool):
    """Display information about a given submission"""
    submission = (
        ctx.obj["db_session"].query(Submission).filter_by(post_id=post_id).one()
    )

    if not submission:
        print("Nothing found!")
    elif filename:
        print(submission.image_filename)
    else:
        print(submission.pprint())


@redwall.command()
@click.pass_context
def list_candidates(ctx):
    """List submissions suitable for the current monitor setup"""
    chooser = Chooser(ctx.obj["db_session"], get_monitors())
    chooser.list_candidates_by_subreddit()


@redwall.command()
@click.pass_context
def random(ctx):
    """Select a random submission suitable for the current monitor setup"""
    chooser = Chooser(ctx.obj["db_session"], get_monitors())
    submission = chooser.get_random_candidate()
    print(submission.image_filename)


@redwall.command()
@click.argument("text", nargs=-1)
@click.pass_context
def search(ctx, text: str):
    """Search for entries by title"""
    submissions = (
        ctx.obj["db_session"]
        .query(Submission)
        .filter(Submission.title.ilike("%{}%".format(" ".join(text))))
        .order_by(Submission.id.asc())
        .all()
    )

    for submission in submissions:
        print(submission.brief())

    print("\n%d result(s) found" % len(submissions))


@redwall.command()
@click.pass_context
def stats(ctx):
    """Display statistics about gathered submissions"""
    display_stats(ctx.obj["db_session"])
