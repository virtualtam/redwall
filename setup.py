#!/usr/bin/env python3
"""Setup script for Redwall"""
import codecs
import os
import re

from setuptools import find_packages, setup


def get_long_description():
    """Reads the main README.rst to get the program's long description"""
    with codecs.open("README.rst", "r", "utf-8") as f_readme:
        return f_readme.read()


def get_program_metadata(attribute):
    """Reads program metadata from the main package's __init__"""
    with open(os.path.join("redwall", "__init__.py"), "r", encoding="utf-8") as f_init:
        return re.search(
            r'^__{attr}__\s*=\s*[\'"]([^\'"]*)[\'"]'.format(attr=attribute),
            f_init.read(),
            re.MULTILINE,
        ).group(1)


setup(
    name=get_program_metadata("title"),
    version=get_program_metadata("version"),
    description="Redwall",
    long_description=get_long_description(),
    author=get_program_metadata("author"),
    author_email="virtualtam@flibidi.net",
    license="MIT",
    url="https://github.com/virtualtam/redwall",
    keywords="image reddit wallpaper",
    packages=find_packages(exclude=["tests.*", "tests"]),
    entry_points={"console_scripts": ["redwall = redwall.cli:redwall"]},
    install_requires=[
        "click>=8.0,<8.1",
        "Pillow>=9.3,<9.4",
        "praw>=7.5.0,<7.6",
        "requests>=2.27,<2.28",
        "screeninfo==0.8",
        "SQLAlchemy>=1.4,<1.5",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
