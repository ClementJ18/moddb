from .pages import *

from typing import List, Union

def search(self, query : str, category : SearchCategory, **filters) -> List[Thumbnail]:
    pass

def parse(self, url : str) -> object:
    pass

class ClientUser:
    def __init__(self, *attrs):
        self.session = requests.Session()

    def login(self, username, password):
        r = requests.get("https://www.moddb.com/members/login")
        soup = BeautifulSoup(r.text, "html.parser")

        payload = {
            soup.find("input", id="membersusername")["name"] : username,
            "password": password,
            "rememberme": 1
        }


        r = self.session.post("https://www.moddb.com/members/login/#membersform", data=payload)
        return r

