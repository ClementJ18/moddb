import sys
import json
import requests
from typing import Union, Any
from robobrowser import RoboBrowser

from .utils import soup, get_type_from, get_date, BASE_URL
from .boxes import Update, Thumbnail, Request, Comment
from .pages import Member, Group, Mod, Game, Engine, Team
from .enums import ThumbnailType, WatchType

class ModdbException(Exception):
    pass

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

    Attributes
    ----------
    member : Member
        The member objects this client instance represents
    """

    def __init__(self, username : str, password : str):
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

        self.member = Member(soup(self._request("get", f"{BASE_URL}/members/{username}").text))

    def __repr__(self):
        return repr(self.member)

    def __enter__(self):
        self._fake_session = sys.modules["moddb"].SESSION
        sys.modules["moddb"].SESSION = self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.modules["moddb"].SESSION = self._fake_session
        delattr(self, "_fake_session")

    def _request(self, method, url, **kwargs):
        """Making sure we do our request with the cookies from this client rather than the cookies
        of the library."""
        route = getattr(requests, method)
        cookies = cookies = requests.utils.dict_from_cookiejar(self._session.cookies)
        r = route(url, cookies=cookies, **kwargs)
        return self._proccess_response(r)

    def _proccess_response(self, r):
        #if we're making an ajax request we'll get a json response that we decode and check for errors
        try:
            text = r.json()
            if text.get("error", False):
                raise ModdbException(text["text"])
        except json.decoder.JSONDecodeError:
            r.raise_for_status()

        return r

    def get_updates(self):
        """Get the current updates the user has for models they are subscribed to.
        
        Returns
        --------
        List[Update]
            List of updates (thumbnail like objects with extra methods and an extra attribute)
        """
        r = self._request("get", f"{BASE_URL}/messages/updates")
        html = soup(r.text)
        updates = []
        
        strings = ("Mods Watch", "Members Watch", "Engines Watch", "Groups Watch", "Games Watch")
        raw = html.find_all("span", string=strings)
        objects = [e.parent.parent.parent.find("div", class_="table").find_all("div", recursive=False) for e in raw]

        objects_raw = [item for sublist in objects for item in sublist[:-1]]
        for update in objects_raw:
            thumbnail = update.find("a")
            unfollow = update.find("a", title="Stop Watching")["href"]
            clear = update.find("a", title="Clear")["href"]
            updates_raw = update.find("p").find_all("a")

            updates.append(Update(
                name=thumbnail["title"], url=thumbnail["href"], type=get_type_from(thumbnail["href"]), 
                image=thumbnail.img["src"], client=self, unfollow=unfollow, clear=clear,
                updates = [Thumbnail(name=x.string, url=x["href"], type=get_type_from(x["href"])) for x in updates_raw],
                date=get_date(update.find("time")["datetime"])
            ))

        return updates

    def get_friend_requests(self):
        """Get the current friend requests the user has.
        
        Returns
        --------
        List[Request]
            List of requests (thumbnail like objects with extra methods)
        """
        r = self._request("get", f"{BASE_URL}/messages/updates")
        html = soup(r.text)
        requests = []
        raw = html.find("span", string="Friend Requests")
        raw_requests = raw.parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)

        for request in raw_requests[:-1]:
            thumbnail = request.find("a")
            accept = request.find("a", title="Accept")["href"]
            decline = request.find("a", title="Decline")["href"]

            requests.append(Request(
                name=thumbnail["title"], url=thumbnail["href"], type=get_type_from(thumbnail["href"]), 
                image=thumbnail.img["src"], client=self, accept=accept, decline=decline,
                date=get_date(request.find("time")["datetime"])
            ))

        return requests

    def get_watched(self, category :  WatchType, page : int = 1):
        """Get a list of thumbnails of watched items based on the type parameters. Eventually, you'll also be
        able to paginate your mods. 

        Parameters
        -----------
        category : WatchType
            The type of watched thing you wanna get (mod, games, engines)
        page : int
            The page number you want to get

        Returns
        --------
        List[Thumbnail]
            List of watched things

        """
        url = f"{BASE_URL}/messages/watching/{category.name}s/page/{page}"
        html = soup(self._request("get", url).text)

        results_raw = html.find("div", class_="table").find_all("div", recursive=False)[1:]
        results = [Thumbnail(url=x.a["href"], name=x.a["title"], type=ThumbnailType[category.name], image=x.a.img["src"]) for x in results_raw]

        return results

    def tracking(self, page : Union[Mod, Game, Engine, Group, Member]):
        """Follow/unfollow this page.
        
        Parameters
        -----------
        page : Union[Mod, Game, Engine, Group, Member]
            The page you wish to watch/unwatch

        Raises
        -------
        ModdbException
            An error has occured while trying to follow/unfollow the page

        Returns
        --------
        bool
            True if the page has been successfully followed, False if it has been successfully unfollowed
        """
        r = self._request("post", f"{BASE_URL}/messages/ajax/action/",
            data = {
                "ajax": "t",
                "action": "watch",
                "sitearea": page.url.split("/")[-2],
                "siteareaid": page.id
            },
            allow_redirects=False
        )

        return "be notified" in r.json()["text"]

    def like_comment(self, comment : Comment):
        """Like a comment, if the comment has already been liked nothing will happen.

        Parameters
        -----------
        comment : Comment
            The comment to like

        Raises
        -------
        ModdbException
            An error has occured while trying to like the comment

        Returns
        --------
        bool
            True if the comment has been successfully liked
        """
        r = self._request("post", f"{BASE_URL}/messages/ajax/action/",
            data = {
                "ajax": "t",
                "action": "karmagood",
                "sitearea": "comment",
                "siteareaid": comment.id
            },
            allow_redirects=False
        )

        return "successfully issued" in r.json()["text"]

    def dislike_comment(self, comment : Comment):
        """Dislike a comment, if the comment has already been disliked nothing will happen.

        Parameters
        -----------
        comment : Comment
            The comment to dislike

        Raises
        -------
        ModdbException
            An error has occured while trying to dislike the comment

        Returns
        --------
        bool
            True if comment has been successfully disliked.
        """
        if not hasattr(comment, "downvote"):
            raise TypeError("Argument must be a Comment-like object")

        r = self._request("post", f"{BASE_URL}/messages/ajax/action/",
            data = {
                "ajax": "t",
                "action": "karmabad",
                "sitearea": "comment",
                "siteareaid": comment.id
            },
            allow_redirects=False
        )

        return "successfully issued" in r.json()["text"]

    def membership(self, page : Union[Group, Team]):
        """Join/leave a team

        Parameters
        -----------
        page : Union[Group, Team]
            The team/group you want to join. Will not work if you don't have permissions

        Raises
        -------
        ModdbException
            An error has occured while trying to join/leave the group/team

        Returns
        --------
        bool
            True if the group/team has been successfully joined, False if the group/team has been
            successfully left.

        """
        r = self._request("post", f"{BASE_URL}/groups/ajax/members/change/{page.id}",
            data = {"ajax": "t"},
            allow_redirects=False
        )

        return "successfully joined" in r.json()["text"]

    def report(self, page : Any):
        """Report a page. This can take any attribute that has an id and url attribute.

        Parameters
        -----------
        page : Any
            The page to report

        Raises
        -------
        ModdbException
            An error has occured while trying to report the page

        Returns
        --------
        bool
            True if the page has been successfully reported
        """
        r = self._request("post", f"{BASE_URL}/messages/ajax/action/",
            data = {
                "ajax": "t",
                "action": "report",
                "sitearea": page.url.split("/")[-2],
                "siteareaid": page.id
            },
            allow_redirects=False
        )

        return not "already reported this content" in r.json()["text"]

    def unfriend(self, member : Member):
        """Unfriend this member if you are friends with them.
        
        Parameters
        -----------
        member : Member
            The member you wish to unfriend

        Raises
        -------
        ModdbException
            An error has occured trying to unfriend this user

        Returns
        --------
        bool
            True if the user was succesfully unfriended
        """
        r = self._request("post", f"{BASE_URL}/members/ajax/friends/delete/{member.id}",
            data = {"ajax": "t"},
            allow_redirects=False
        )

        return "no longer friends with this member" in r.json()["text"]

    def send_request(self, member :  Member):
        """Send a friend request to a user. You will not instantly become friends with them,
        they will have to accept the friend request you sent them first.
        
        Parameters
        -----------
        member : Member
            The member you wish to send a friend request to

        Raises
        -------
        ModdbException
            An error has occured trying to send a friend request to that user

        Returns
        --------
        bool
            True if the user was succesfully sent a friend request
        """
        r = self._request("post", f"{BASE_URL}/members/ajax/friends/add/{member.id}",
            data = {"ajax": "t"},
            allow_redirects=False
        )

        return "friend request has been sent" in r.json()["text"]
