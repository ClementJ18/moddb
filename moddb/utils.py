import datetime
import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import logging
import sys

LOGGER = logging.getLogger("moddb")
BASE_URL = "https://www.moddb.com"

def get_date(d):
    try:
        return datetime.datetime.strptime(d[:-3] + d[-2:], '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(d, '%Y-%m-%d')
    except ValueError:
        pass

    return datetime.datetime.strptime(d, '%Y-%m')

def soup(url):
    SESSION = sys.modules["moddb"].SESSION
    cookies = requests.utils.dict_from_cookiejar(SESSION.cookies)
    r = SESSION.get(url, cookies=cookies)
    html = BeautifulSoup(r.text, "html.parser")
    return html

def get_views(string):
    matches = re.search(r"^([0-9,]*) \(([0-9,]*) today\)$", string)
    views = int(matches.group(1).replace(",", ""))
    today = int(matches.group(2).replace(",", ""))

    return views, today

def join(path):
    return urljoin(BASE_URL, path)

def normalize(string):
    return string.replace(",", "").replace("members", "").replace("member", "")

def get_type(img):
    if img is None:
        return 2
    elif img["src"][-8:-5] == ".mp4":
        return 0
    else:
        return 1
