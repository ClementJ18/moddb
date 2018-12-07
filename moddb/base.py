from typing import List
from .enums import SearchCategory
from .boxes import Thumbnail
from .utils import soup, SESSION

def search(self, query : str, category : SearchCategory, **filters) -> List[Thumbnail]:
    pass

def parse(self, url : str) -> object:
    pass


def login(username, password):
    html = soup("https://www.moddb.com/members/login")

    payload = {
        html.find("input", id="membersusername")["name"] : username,
        "password": password,
        "rememberme": 1
    }

    r = SESSION.post("https://www.moddb.com/members/login/#membersform", data=payload)
    print(r.cookies)

    return username in r.text, r

