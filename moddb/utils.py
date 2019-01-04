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

def get_tags(html):
    """Helper function to return the tags found on a page"""
    #ToDo
    pass

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

def soup(url : str, *, params : dict = {}) -> BeautifulSoup:
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
    SESSION = sys.modules["moddb"].SESSION
    cookies = requests.utils.dict_from_cookiejar(SESSION.cookies)

    r = SESSION.get(url, cookies=cookies, params=params)
    html = BeautifulSoup(r.text, "html.parser")

    return html

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
    """Joins a partial moddb string with the base url and returns the combined url"""
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
        
class Object:
    """A dud objects that will transform every kwarg given into an attribute"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

