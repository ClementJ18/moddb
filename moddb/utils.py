import datetime
import re
from urllib.parse import urljoin

BASE_URL = "https://www.moddb.com"

def get_date(d):
    d = d[:-3] + d[-2:]

    return datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S%z')

def get_views(string):
    matches = re.search(r"^([0-9,]*) \(([0-9,]*) today\)$", string)
    views = int(matches.group(1).replace(",", ""))
    today = int(matches.group(2).replace(",", ""))

    return views, today

def join(path):
    return urljoin(BASE_URL, path)
