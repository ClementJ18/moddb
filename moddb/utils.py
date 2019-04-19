from .enums import ThumbnailType

import re
import sys
import logging
import datetime
import requests
from typing import Tuple
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin
import inspect

LOGGER = logging.getLogger("moddb")
BASE_URL = "https://www.moddb.com"

def concat_docs(cls):
    """Does it look like I'm enjoying this?"""
    attributes = []

    def get_docs(parent):
        nonlocal attributes
        if parent.__name__ == 'object':
            return

        docs = parent.__doc__.splitlines()
        if "    Attributes" in docs:
            attributes = docs[docs.index("    Attributes") + 2:] + attributes

        source = inspect.getsource(parent.__init__)
        source = source[source.index('):'):]

        if 'super().__init__' in source:
            get_docs(parent.__base__)
        elif '__init__' in source:
            get_docs(parent.__base__.__base__)            

    get_docs(cls)
    original = cls.__doc__.splitlines()
    if not "    Attributes" in original:
        original.append("    Attributes")
        original.append("    -----------")

    final = original[:original.index("    Attributes") + 2]
    final.extend([x for x in attributes if x.strip()])
    cls.__doc__ = "\n".join(final)

    return cls

def get_date(d : str) -> datetime.datetime:
    """A helper function that takes a ModDB string representation of time and returns an equivalent 
    datetime.datetime object. This can range from a datetime with the full year to
    second to just a year and a month. 

    Parameters
    -----------
    d : str
        String representation of a datetime

    Returns
    -------
    datetime.datetime
        The datetime object for the given string
    """ 
    try:
        return datetime.datetime.strptime(d[:-3] + d[-2:], '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(d, '%Y-%m-%d')
    except ValueError:
        pass

    return datetime.datetime.strptime(d, '%Y-%m')

def request(url, *, params = {}, post = False):
    """Helper function to make get/post requests with the current SESSION object.

    Parameters
    -----------
    url : str
        url to get
    params : dict
        A dict of paramaters to be passed along
    post : bool
        Whether or not this a post request

    Return
    -------
    requests.Response
        The returned response object

    """
    SESSION = sys.modules["moddb"].SESSION
    cookies = requests.utils.dict_from_cookiejar(SESSION.cookies)
    if "query" in params:
        params["query"] = params["query"].replace(" ", "+")

    if post:
        r = SESSION.post(url, data=params.get("data", {}), cookies=cookies)
    else:
        r = SESSION.get(url, cookies=cookies, params=params)

    r.raise_for_status()
    return r

def soup(html : str) -> BeautifulSoup:
    """Simple helper function that takes a string representation of an html page and
    returns a beautiful soup object"""
    
    soup = BeautifulSoup(html, "html.parser")
    return soup

def get_page(url : str, *, params : dict = {}):
    """A helper function that takes a url and returns a beautiful soup objects. This is used to center
    the request making section of the library. Can also be passed a set of paramaters, used for sorting
    and filtering in the search function.

    Parameters
    -----------
    url : str
        The url to get

    params : dict
        A dictionnary of filters and sorting key-value pairs.

    Returns
    -------
    bs4.BeautifulSoup
    """
    r = request(url, params=params)
    return soup(r.text)

def get_views(string : str) -> Tuple[int, int]:
    """A helper function that takes a string reresentation of total something and
    daily amount of that same thing and returns both as a tuple of ints.

    Parameters
    ------------
    string : str
        The string containing the numbers both total and daily

    Returns
    --------
    Tuple[int, int]
        Tuple contains the total views (first element) and the daily views (second element)
    """
    matches = re.search(r"^([0-9,]*) \(([0-9,]*) today\)$", string)
    views = int(matches.group(1).replace(",", ""))
    today = int(matches.group(2).replace(",", ""))

    return views, today

def join(path : str) -> str:
    """Joins a partial moddb url with the base url and returns the combined url
    
    Parameters
    -----------
    path : str
        the url to join

    Return
    -------
    str
        The full url.

    """
    return urljoin(BASE_URL, path)

def normalize(string : str) -> str:
    """Removes all extra fluff from a text to get the barebone content"""
    return string.replace(",", "").replace("members", "").replace("member", "").strip()

def get_type(img : Tag) -> int:
    """Determines the type of the image through some very hacky stuff, might break"""
    if img is None:
        return 2
    elif img["src"][-8:-5] == ".mp4":
        return 0
    else:
        return 1 

def get_type_from(url):
    """Get the page type based on a url.

    Parameters
    -----------
    url : str
        The url to get 

    Return
    -------
    ThumbnailType
        The type of the page
    """
    regex = r"\/([a-z]+)\/"
    type_mapping = {
        "new": "article",
        "feature": "article",
        "tutorial": "article",
        "download": "file",
        "image": "media",
        "audio": " media",
        "video": "media"
    }

    matches = re.findall(regex, url)
    matches.reverse()
    match = matches[0][0:-1] if matches[0].endswith("s") else matches[0]      

    try:
        page_type = ThumbnailType[match]
    except KeyError:
        page_type = ThumbnailType[type_mapping[match]]

    LOGGER.info("%s is type %s", url, page_type)
    return page_type

def get_page_number(html):
    try:
        max_page = int(html.find("div", class_="pages").find_all()[-1].string)
    except AttributeError:
        LOGGER.info("Has less than 30 comments (only one page)")
        max_page = 1

    try:
        page = int(html.find("span", class_="current").string)
    except AttributeError:
        LOGGER.info("Has less than 30 results (only one page)")
        page = 1

    return page, max_page
        
class Object:
    """A dud objects that will transform every kwarg given into an attribute"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

time_mapping = {
    "year" : 125798400,
    "month": 2419200,
    "week": 604800,
    "day": 86400,
    "hour": 3600,
    "minute": 60,
    "econd": 1
}
