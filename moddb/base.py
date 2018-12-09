from .enums import SearchCategory, ThumbnailType
from .boxes import Thumbnail
from .utils import soup, LOGGER

import re
import sys
from typing import List
from robobrowser import RoboBrowser
from collections import Counter

def search(query : str, category : SearchCategory, **filters) -> List[Thumbnail]:
    pass

def parse(url : str, *, page_type : ThumbnailType = None) -> object:
    regex = r"\/([a-z]+)\/"
    html = soup(url)

    type_mapping = {
        "new": "article"
    }

    if page_type is None:
        page_url = html.find("meta", property="og:url")["content"]
        matches = re.findall(regex, page_url)
        matches.reverse()
        match = matches[0][0:-1] if matches[0].endswith("s") else matches[0]      

        try:
            page_type = ThumbnailType[match]
        except KeyError:
            page_type = ThumbnailType[type_mapping[match]]

        LOGGER.info("%s is type %s", url, page_type)

    model = getattr(sys.modules["moddb"], page_type.name.title())(html)
    return model


def login(username, password):
    browser = RoboBrowser(history=True, parser='html.parser')
    browser.open('https://www.moddb.com/members/login')
    t = browser.find_all("form")[1].find_all("input", class_="text", type="text")
    t.remove(browser.find("input", id="membersusername"))
    form = browser.get_form(attrs={"name": "membersform"})

    form["password"].value = password
    form["referer"].value = ""
    form[browser.find("input", id="membersusername")["name"]].value = username
    form[t[0]["name"]].value = ""

    browser.submit_form(form)
    sys.modules["moddb"].SESSION = browser.session

    if not "freeman" in browser.session.cookies:
        raise ValueError(f"Login failed for user {username}")

def logout():
    sys.modules["moddb"].SESSION.cookies.clear()
