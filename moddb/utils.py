import datetime
import re
from urllib.parse import urljoin

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
    elif img["src"].endswith(("png", "jpg")):
        return 1
