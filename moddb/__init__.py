from .base import search, parse, login
from .pages import *
from .utils import LOGGER, BASE_URL, soup
from .enums import SearchCategory

import requests
SESSION = requests.Session()

__version__ = "0.0.1"
