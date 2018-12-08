from .enums import SearchCategory
from .boxes import Thumbnail
from .utils import soup

import sys
from typing import List
from robobrowser import RoboBrowser

def search(self, query : str, category : SearchCategory, **filters) -> List[Thumbnail]:
    pass

def parse(self, url : str) -> object:
    pass


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
