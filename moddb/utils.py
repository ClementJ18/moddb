from .enums import ThumbnailType

import re
import sys
import uuid
import random
import inspect
import logging
import datetime
import requests
from typing import Tuple
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag

LOGGER = logging.getLogger("moddb")
BASE_URL = "https://www.moddb.com"

time_mapping = {
    "year" : 125798400,
    "month": 2419200,
    "week": 604800,
    "day": 86400,
    "hour": 3600,
    "minute": 60,
    "econd": 1
}

user_agent_list = [
    #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    #Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]

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
        r = SESSION.post(url, data=params.get("data", {}), cookies=cookies, headers={"User-Agent": random.choice(user_agent_list)})
    else:
        r = SESSION.get(url, cookies=cookies, params=params, headers={"User-Agent": random.choice(user_agent_list)})

    r.raise_for_status()
    return r

def soup(html : str) -> BeautifulSoup:
    """Simple helper function that takes a string representation of an html page and
    returns a beautiful soup object"""
    
    soupd = BeautifulSoup(html, "html.parser")
    return soupd

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
    regex = r"\/((?!page|pages\b)\b\w+)\/"
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
    match = matches[-1][0:-1] if matches[0].endswith("s") else matches[0]      

    try:
        page_type = ThumbnailType[match]
    except KeyError:
        page_type = ThumbnailType[type_mapping[match]]

    LOGGER.info("%s is type %s", url, page_type)
    return page_type

def get_page_number(html):
    """Central function for retrieving the page numbers of result pages

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to get the page numbers from

    Returns
    --------
    Tuple[int, int]
        The page and max_page
    """
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

def find(predicate, seq):
    """A helper to return the first element found in the sequence
    that meets the predicate. For example: ::

        comment = find(lambda comment: comment.author.name == 'SilverElf', mod.comments.flatten())

    would find the first :class:`.Comment` whose author's name is 'SilverElf' and return it.
    If no entry is found, then ``None`` is returned.

    This is different from `filter`_ due to the fact it stops the moment it finds
    a valid entry.

    .. _filter: https://docs.python.org/3.6/library/functions.html#filter

    Parameters
    -----------
    predicate
        A function that returns a boolean-like result.
    seq : iterable
        The iterable to search through.
    """

    for element in seq:
        if predicate(element):
            return element
    return None

def get(iterable, **attrs):
    r"""A helper that returns the first element in the iterable that meets
    all the traits passed in ``attrs``. This is an alternative for
    :func:`moddb.utils.find`.

    When multiple attributes are specified, they are checked using
    logical AND, not logical OR. Meaning they have to meet every
    attribute passed in and not one of them.

    To have a nested attribute search (i.e. search by ``x.y``) then
    pass in ``x__y`` as the keyword argument.

    If nothing is found that matches the attributes passed, then
    ``None`` is returned.

    Examples
    ---------

    Basic usage:

    .. code-block:: python3

        article = moddb.utils.get(mod.get_articles(), name='Version 3.5 Released')

    Multiple attribute matching:

    .. code-block:: python3

        comment = moddb.utils.get(mod.get_comments(2), content='Test', karma=3)

    Nested attribute matching:

    .. code-block:: python3

        comment = moddb.utils.get(article.get_comments(), author__name='SilverElf', content='Best article ever')

    Parameters
    -----------
    iterable
        An iterable to search through.
    \*\*attrs
        Keyword arguments that denote attributes to search with.
    """

    def predicate(elem):
        for attr, val in attrs.items():
            nested = attr.split('__')
            obj = elem
            for attribute in nested:
                obj = getattr(obj, attribute)

            if obj != val:
                return False
        return True

    return find(predicate, iterable)

def generate_hash():
    return uuid.uuid4().hex
