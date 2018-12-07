from typing import List, Union
from .enums import SearchCategory
from .boxes import Thumbnail

def search(self, query : str, category : SearchCategory, **filters) -> List[Thumbnail]:
    pass

def parse(self, url : str) -> object:
    pass


def login(username, password):
    r = requests.get("https://www.moddb.com/members/login")
    soup = BeautifulSoup(r.text, "html.parser")

    payload = {
        soup.find("input", id="membersusername")["name"] : username,
        "password": password,
        "rememberme": 1
    }

    r = SESSION.post("https://www.moddb.com/members/login/#membersform", data=payload)
    print(r.cookies)

    return username in r.text, r

