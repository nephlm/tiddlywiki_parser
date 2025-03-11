#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="tiddlywiki_parser",
    version="0.1.1",
    packages=find_packages(),
    install_requires=["beautifulsoup4>=4.8.0", "requests>=2.22.0"],
    entry_points={"console_scrips": ["tiddlywiki_parser = tiddlywiki_parser:main"]},
)
