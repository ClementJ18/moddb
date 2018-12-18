from .base import search, parse, login, logout
from .pages import *
from .utils import LOGGER, BASE_URL, soup, Object
from .enums import *

import requests
SESSION = requests.Session()

__version__ = "0.0.1"
