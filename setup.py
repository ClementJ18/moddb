#!/usr/bin/env python

from setuptools import setup

setup(name = "moddb",
    version = "0.2",
    description = "A scrapper for ModDB Mod and Game pages",
    author = "Clement Julia",
    author_email = "clement.julia13@gmail.com",
    url = "https://github.com/ClementJ18/moddb",
    packages = ["moddb"],
    install_requires=[
        'beautifulsoup4 == 4.6.3',
        'requests>=2.20.0',
        'robobrowser == 0.5.3'
      ]
    )