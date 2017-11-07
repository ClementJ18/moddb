#!/usr/bin/env python

from setuptools import setup

setup(name = "ModDB Reader",
    version = "0.3",
    description = "A scrapper for ModDB Mod and Game pages",
    author = "Clement Julia",
    author_email = "clement.julia13@gmail.com",
    url = "https://github.com/ClementJ18/moddb_reader",
    packages = ["moddb_reader", "moddb_parser", "moddb_objects"])