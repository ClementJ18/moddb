from .base import search, parse, login, logout, front_page
from .utils import LOGGER, BASE_URL, soup, request, get_page, Object
from .enums import *
from .pages import *
#remove get_reviews from Group, Company

import requests
SESSION = requests.Session()

__version__ = "0.0.1"
