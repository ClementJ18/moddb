import requests
from robobrowser import RoboBrowser

from .utils import soup, get_type_from, get_date, BASE_URL, get_page
from .boxes import Update, Thumbnail
from .pages import Member

class Client:
    """Login the user to moddb through the library, this allows user to see guest comments and see
    private groups they are part of. In addition, this can be used for a lot of the operation 

    Parameters
    -----------
    username : str
        The username of the user

    password : str
        The password associated to that username

    Raises
    -------
    ValueError
        The password or username was incorrect
    """

    def __init__(self, username, password):
        browser = RoboBrowser(history=True, parser='html.parser')
        browser.open(f'{BASE_URL}/members/login')
        t = browser.find_all("form")[1].find_all("input", class_="text", type="text")
        t.remove(browser.find("input", id="membersusername"))
        form = browser.get_form(attrs={"name": "membersform"})

        form["password"].value = password
        form["referer"].value = ""
        form[browser.find("input", id="membersusername")["name"]].value = username
        form[t[0]["name"]].value = ""

        browser.submit_form(form)
        self._session = browser.session

        if "freeman" not in browser.session.cookies:
            raise ValueError(f"Login failed for user {username}")

        self.member = Member(get_page(f"{BASE_URL}/members/{username}"))

    def _request(self, method, url, **kwargs):
        route = getattr(requests, method)
        cookies = cookies = requests.utils.dict_from_cookiejar(self._session.cookies)
        r = route(url, cookies=cookies, **kwargs)
        return r

    def get_updates(self):
        """Get the current updates the user has for models they are subscribed to.
        
        Returns
        --------
        List[Update]
            List of updates (thumbnail like objects with extra methods)
        """
        r = self._request("get", "https://www.moddb.com/messages/updates")
        html = soup(r.text)
        updates = []
        
        strings = ("Mods Watch", "Members Watch", "Engines Watch", "Groups Watch", "Games Watch")
        raw = html.find_all("span", string=strings)
        objects = [e.parent.parent.parent.find("div", class_="table").find_all("div", recursive=False) for e in raw]

        objects_raw = [item for sublist in objects for item in sublist[:-1]]
        for update in objects_raw:
            thumbnail = update.find("a")
            url = thumbnail["href"]
            title = thumbnail["title"]
            image = thumbnail.img["src"]
            page_type = get_type_from(url)
            unfollow = update.find("a", title="Stop Watching")["href"]
            clear = update.find("a", title="Clear")["href"]
            updates_raw = update.find("p").find_all("a")

            updates.append(Update(
                name=title, url=url, type=page_type, image=image, 
                client=self, unfollow=unfollow, clear=clear,
                updates = [Thumbnail(name=x.string, url=x["href"], type=get_type_from(x["href"])) for x in updates_raw],
                date = get_date(update.find("time")["datetime"])
            ))

        return updates
