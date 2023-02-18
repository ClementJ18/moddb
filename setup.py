#!/usr/bin/env python

from pkg_resources import parse_requirements
from setuptools import setup, find_packages
import re

version = ""
with open("moddb/__init__.py") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError("version is not set")

readme = ""
with open("README.md") as f:
    readme = f.read()

install_requires = []
with open("requirements.txt") as f:
    install_requires = [str(requirement) for requirement in parse_requirements(f)]

setup(
    name="moddb",
    version=version,
    description="A scrapper for ModDB Mod and Game pages",
    author="Clement Julia",
    author_email="clement.julia13@gmail.com",
    url="https://github.com/ClementJ18/moddb",
    long_description_content_type="text/markdown",
    long_description=readme,
    packages=find_packages(include=["moddb", "moddb.*"]),
    install_requires=install_requires,
)
