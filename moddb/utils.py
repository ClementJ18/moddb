import datetime
import functools
import inspect
import logging
import random
import re
import ssl
import sys
import time
import uuid
from typing import Optional, Sequence, Tuple, TypeVar
from urllib.parse import urljoin

import bs4
import requests
from bs4 import BeautifulSoup, Tag
from requests import utils

from .enums import MediaCategory, ThumbnailType
from .errors import AuthError, AwaitingAuthorisation, ModdbException, Ratelimited

LOGGER = logging.getLogger("moddb")
BASE_URL = "https://www.moddb.com"


time_mapping = {
    "year": 125798400,
    "month": 2419200,
    "week": 604800,
    "day": 86400,
    "hour": 3600,
    "minute": 60,
    "econd": 1,
}

user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.2792.65",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox One) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edge/44.18363.8131",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 OPR/114.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 OPR/114.0.0.0",
]


def concat_docs(cls):
    """Does it look like I'm enjoying this?"""
    attributes = []

    def get_docs(parent):
        nonlocal attributes
        if parent.__name__ == "object":
            return

        docs = parent.__doc__.splitlines()
        if "    Attributes" in docs:
            attributes = docs[docs.index("    Attributes") + 2 :] + attributes

        source = inspect.getsource(parent.__init__)
        source = source[source.index("):") :]

        if "super().__init__" in source:
            get_docs(parent.__base__)
        elif "__init__" in source:
            get_docs(parent.__base__.__base__)

    get_docs(cls)
    original = cls.__doc__.splitlines()
    if "    Attributes" not in original:
        original.append("    Attributes")
        original.append("    -----------")

    final = original[: original.index("    Attributes") + 2]
    final.extend([x for x in attributes if x.strip()])
    cls.__doc__ = "\n".join(final)

    return cls


class SSLAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ssl_context = ssl.create_default_context()
        ssl_context.maximum_version = ssl.TLSVersion.TLSv1_2

        kwargs["ssl_context"] = ssl_context
        return super().init_poolmanager(*args, **kwargs)


class Ratelimit:
    def __init__(self, rate: float, per: float, sleep: Optional[None] = None):
        self.rate = rate
        self.per = per
        self.sleep = sleep

        self.last_called = datetime.datetime.min
        self.initial_call = datetime.datetime.min
        self.call_count = 0

    def reset(self, now: datetime.datetime = None):
        if now is None:
            now = datetime.datetime.now()

        self.initial_call = now
        self.call_count = 0

    def call(self):
        now = datetime.datetime.now()

        expiry = self.initial_call + datetime.timedelta(seconds=self.per)
        if now > expiry:
            LOGGER.info("Resetting ratelimit")
            self.reset(now)

        if self.call_count + 1 > self.rate:
            remaining = (expiry - now).total_seconds()
            if self.sleep is not None and remaining <= self.sleep:
                LOGGER.info("Ratelimited! Sleeping for %s", remaining)
                time.sleep(remaining)
                self.reset(now)
            else:
                raise Ratelimited(f"Ratelimited please try again in {remaining}", remaining)

        self.call_count += 1


def ratelimit(*limiters: Ratelimit):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for limiter in limiters:
                limiter.call()

            return func(*args, **kwargs)

        return wrapper

    return decorator


GLOBAL_LIMITER = Ratelimit(40, 300, sleep=300)
GLOBAL_THROTLE = Ratelimit(5, 1, sleep=1)
COMMENT_LIMITER = Ratelimit(1, 60)
LOGIN_LIMITER = Ratelimit(1, 5)


def get_date(d: str) -> datetime.datetime:
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
        return datetime.datetime.strptime(d[:-3] + d[-2:], "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(d, "%Y-%m-%d")
    except ValueError:
        pass

    return datetime.datetime.strptime(d, "%Y-%m")


def prepare_request(req: requests.Request, session: requests.Session):
    """Prepared a request with the appropriate cookies"""
    cookies = utils.dict_from_cookiejar(session.cookies)

    if req.cookies is not None:
        req.cookies = {**req.cookies, **cookies}
    else:
        req.cookies = cookies

    if "User-Agent" not in req.headers:
        req.headers["User-Agent"] = random.choice(user_agent_list)

    return session.prepare_request(req)


def raise_for_status(response: requests.Response):
    """Raise any error that could have occured"""
    try:
        text = response.json()
        if text.get("error", False):
            LOGGER.error(text["text"])
            LOGGER.error(response.request.url)
            LOGGER.error(response.request.body)
            raise ModdbException(text["text"])
    except requests.exceptions.JSONDecodeError:
        pass

    response.raise_for_status()

    if (
        "is currently awaiting authorisation, which can take a couple of days while a"
        in response.text.lower()
    ):
        raise AwaitingAuthorisation(
            "This page is still await authorisation and cannot currently be parsed"
        )


@ratelimit(LOGIN_LIMITER)
def generate_login_cookies(username: str, password: str, session: requests.Session = None):
    """Log a user in and return the `freeman` cookie containing the login hash"""
    if session is None:
        session = sys.modules["moddb"].SESSION

    data, resp = create_login_payload(username, password, session)

    req = requests.Request("POST", f"{BASE_URL}/members/login", data=data, cookies=resp.cookies)
    login = session.send(prepare_request(req, session), allow_redirects=False)

    if "members2faemailhash" in login.text:
        raise AuthError("2FA required, use TwoFactorAuthClient")

    if "freeman" not in login.cookies:
        raise ValueError(f"Login failed for user {username}")

    return login.cookies


def create_login_payload(username: str, password: str, session: requests.Session):
    req = requests.Request("GET", f"{BASE_URL}/members/login")
    resp = session.send(prepare_request(req, session))
    resp.raise_for_status()

    html = soup(resp.text)
    form = html.find("form", attrs={"name": "membersform"})

    username_input = form.find("input", id="membersusername")
    botcatcher = form.find("input", type="text", id=False)

    data = {
        "referer": "",
        username_input["name"]: username,
        botcatcher["name"]: "",
        "password": password,
        "rememberme": ["1"],
        "members": "Sign in",
    }

    return data, resp


@ratelimit(GLOBAL_THROTLE, GLOBAL_LIMITER)
def request(req: requests.Request):
    """Helper function to make get/post requests with the current SESSION object.

    Parameters
    -----------
    req : requests.Request
        The request to perform

    Returns
    -------
    requests.Response
        The returned response object

    """
    session: requests.Session = sys.modules["moddb"].SESSION
    prepped = prepare_request(req, session)
    resp = session.send(prepped)

    raise_for_status(resp)
    return resp


def soup(html: str) -> BeautifulSoup:
    """Simple helper function that takes a string representation of an html page and
    returns a beautiful soup object

    Parameters
    -----------
    html : str
        The string representationg of the html to parse

    Returns
    --------
    bs4.BeautifulSoup
        The parsed html
    """

    return BeautifulSoup(html, "html.parser")


def get_page(url: str, *, params: dict = {}, json: bool = False):
    """A helper function that takes a url and returns a beautiful soup objects. This is used to center
    the request making section of the library. Can also be passed a set of paramaters, used for sorting
    and filtering in the search function.

    Parameters
    -----------
    url : str
        The url to get
    params : dict
        A dictionnary of filters and sorting key-value pairs.
    json : Optional[bool]
        Whether the expected response is json, in which case it will not be soup'd

    Returns
    -------
    bs4.BeautifulSoup
        The parsed html
    """
    resp = request(requests.Request("GET", url, params=params))
    if json:
        return resp.json()

    return soup(resp.text)


def get_views(string: str) -> Tuple[int, int]:
    """A helper function that takes a string representation of total something and
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


def join(path: str) -> str:
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
    if not path.startswith(BASE_URL):
        return urljoin(BASE_URL, path)

    return path


def normalize(string: str) -> str:
    """Removes all extra fluff from a stat to get the barebone content.

    Stats usually have extra words like "members" or "visitors" and have command separated integers.

    Parameters
    -----------
    string : str
        The string to clean up

    Returns
    --------
    str
        The cleaned up stat
    """
    return string.replace(",", "").replace("members", "").replace("member", "").strip()


def get_media_type(img: Tag) -> MediaCategory:
    """Determines whether a media is an image, a video or an audio.

    This is somewhat of a brittle method, don't rely on it too much.

    Parameters
    -----------
    img: bsa.Tag
        The image to check

    Returns
    ---------
    MediaCategory
        The category of the media
    """
    if img is None:
        return MediaCategory.audio
    elif img["src"][-8:-5] == ".mp4":
        return MediaCategory.video
    else:
        return MediaCategory.image


def get_page_type(url: str) -> "ThumbnailType":
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
        "video": "media",
    }

    matches = re.findall(regex, url)
    match = matches[-1][0:-1] if matches[0].endswith("s") else matches[0]

    try:
        page_type = ThumbnailType[match]
    except KeyError:
        page_type = ThumbnailType[type_mapping[match]]

    LOGGER.info("%s is type %s", url, page_type)
    return page_type


def ceildiv(a: int, b: int) -> int:
    "Like a // b but rounded up instead of down."
    return -(a // -b)


def get_list_stats(result_box: bs4.BeautifulSoup, per_page: int = 30) -> Tuple[int, int, int]:
    """Get the current page, total pages and total results from
    a result list

    Parameters
    ------------
    result_box: bs4.BeautifulSoup
        The HTML of the result box from a list of results page
    per_page: Optional[int]
        The number of results per page, important for calculations. Defaults
        to 30, doesn't usually need to be touched

    Returns
    --------
    Tuple[int, int, int]
        The stats in order of: number of current page (starting from 1),
        total number of pages (between 1 and X) and the total results.
    """
    stats = re.match(
        r".*\(([0-9,]*) - ([0-9,]*) of ([0-9,]*)\)",
        result_box.find("div", class_="normalcorner")
        .find("div", class_="title")
        .find("span", class_="heading")
        .string,
    )

    if not stats:  # less than a page
        return 1, 1, None

    max_results = int(stats.group(2).replace(",", ""))
    all_results = int(stats.group(3).replace(",", ""))
    max_page = ceildiv(all_results, per_page)
    current_page = ceildiv(max_results, per_page)

    return current_page, max_page, all_results


class Object:
    """A dud objects that will transform every kwarg given into an attribute"""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


D = TypeVar("D")


def find(predicate, seq: Sequence[D]) -> Optional[D]:
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


def get(iterable: Sequence[D], **attrs) -> Optional[D]:
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
            nested = attr.split("__")
            obj = elem
            for attribute in nested:
                obj = getattr(obj, attribute)

            if obj != val:
                return False
        return True

    return find(predicate, iterable)


def generate_hash():
    return uuid.uuid4().hex


def get_sitearea(url: str) -> str:
    """Get the site area from a url"""
    return url.split("/")[-2]


siteareaid_mapping = {
    "3": "mods",
    "2": "games",
}


def get_siteareaid(key: str):
    """Get the sitearea id from an int"""
    return siteareaid_mapping.get(str(key), "none")


number_mapping = {"k": 1_000, "m": 1_000_000}


def unroll_number(string: str) -> int:
    identifier = string[-1].lower()
    if identifier.isdigit():
        return int(string)

    number = float(string[:-1]) * number_mapping[identifier]
    return int(number)
