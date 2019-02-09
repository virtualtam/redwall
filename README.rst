Redwall - The front wallpaper to your monitor(s)
================================================

Redwall is a command-line tool that helps you build a collection of curated
images obtained from Reddit submissions.


Configuration
-------------

Redwall relies on PRAW to get content from Reddit, so you should obtain the
proper credentials, see:

- `Reddit application preferences <https://www.reddit.com/prefs/apps/>`_
- `Authenticating via OAuth
  <https://praw.readthedocs.io/en/latest/getting_started/authentication.html>`_

Once you have registered an application, create a configuration file that should
be located at ``~/.config/redwall.ini``:

::

   [reddit]
   user_agent    = Comment Extraction (by /u/dystopiaGnostalgic)
   client_id     = s0m3cli  # Reddit OAuth client ID
   client_secret = s3rk3t   # Reddit OAuth client secret

   [redwall]
   data_dir = /home/dystopia/redwall/data
   submission_limit = 20
   time_filter      = month
   # dat pr0n
   subreddits =
       AerialPorn
       CityPorn
       EarthPorn
       SpacePorn
       WaterPorn

This file defines authentication information, as well as which subreddits should
be browsed when gathering submitted images.

Take a look at the following threads to find more interesting content ;-)

- `List of Art subreddits
  <https://www.reddit.com/r/redditlists/comments/141nga/list_of_art_subreddits/>`_
- `What are the best photo-based subreddits?
  <https://www.reddit.com/r/AskReddit/comments/4i3rby/what_are_the_best_photobased_subreddits/>`_
- `A list of all photography related subreddits?
  <https://www.reddit.com/r/photography/comments/15xui8/a_list_of_all_photography_related_subreddits/>`\


Installation
------------

To install the latest version of Redwall in a virtualenv:

::

   $ virtualenv ~/.virtualenvs/redwall
   $ source ~/.virtualenvs/redwall/bin/activate
   $ pip install git+https://github.com/virtualtam/redwall.git


Usage
-----

The command-line interface is still pretty much a work in progress and is bound
to change a bit, so the recommended way is to rely on the built-in help:

::

   usage: redwall [-h] [-c CONFIG]
                  {current,gather,history,list-candidates,random,stats} ...

   Redwall helps you manage a collection of curated wallpapers, courtesy of the
   Reddit community

   positional arguments:
     {current,gather,history,list-candidates,random,stats}
                           Command to run
       current             Display information about the currently selected entry
       gather              Gather submission media from Reddit
       history             Display the history of selected entries
       list-candidates     List submissions suitable for the current monitor
                           setup
       random              Select a random submission suitable for the current
                           monitor setup and print its path
       stats               Display statistics about gathered submissions

   optional arguments:
     -h, --help            show this help message and exit
     -c CONFIG, --config CONFIG
                           Configuration file

   ~ The front wallpaper of your computer ~


Libraries
---------

- `Pillow <https://python-pillow.org/>`_, the Python Imaging Library
- `PRAW <https://praw.readthedocs.io/en/latest/>`_, the Python Reddit API
  Wrapper
- `Screeninfo <https://github.com/rr-/screeninfo>`_
- `SQLAlchemy <https://www.sqlalchemy.org/>`_, the Python SQL Toolkit and Object
  Relational Mapper


License
-------

Redwall is licenced under the MIT License.
