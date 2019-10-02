#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="tiddlywiki_parser",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["beautifulsoup4>=4.8.0", "requests>=2.22.0"],
)
