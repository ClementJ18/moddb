#!/usr/bin/env python

from setuptools import setup, find_packages
import re

version = ''
with open('moddb/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

readme = ''
with open('README.md') as f:
    readme = f.read()
  
setup(
    name = "moddb",
    version = version,
    description = "A scrapper for ModDB Mod and Game pages",
    author = "Clement Julia",
    author_email = "clement.julia13@gmail.com",
    url = "https://github.com/ClementJ18/moddb",
    long_description_content_type="text/markdown",
    long_description=readme,
    packages=find_packages(include=['moddb', 'moddb.*']),
    install_requires=[
        'beautifulsoup4 == 4.6.3',
        'requests>=2.20.0',
        'robobrowser == 0.5.3',
        'feedparser == 6.0.10',
        'toolz == 0.11.2',
        'Werkzeug==0.16.1',
        'pyrate-limiter==2.8.1'
      ]
    )