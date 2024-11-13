import requests

from .base import front_page, login, logout, parse_page, parse_results, rss, search, search_tags
from .client import Client, Thread
from .enums import *
from .pages import *
from .utils import BASE_URL, LOGGER, Object, get_page, request, soup, SSLAdapter

SESSION = requests.Session()
SESSION.mount("https://", SSLAdapter())

__version__ = "0.12.0"

__all__ = [
    "front_page",
    "login",
    "logout",
    "parse_page",
    "parse_results",
    "rss",
    "search",
    "search_tags",
    "Client",
    "Thread",
    "BASE_URL",
    "LOGGER",
    "Object",
    "get_page",
    "request",
    "soup",
]
