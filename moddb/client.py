import sys
import json
import time
import random
import requests
from robobrowser import RoboBrowser

from .utils import soup, get_type_from, get_date, BASE_URL, get_page_number, generate_hash, get, LOGGER, user_agent_list
from .boxes import Update, Thumbnail, Request, Comment, ResultList
from .pages import Member, Group, Mod, Game, Engine, Team
from .enums import ThumbnailType, WatchType, Status
from .errors import ModdbException
from .base import parse

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

        LOGGER.info("Login successful for %s", username)

        self.member = Member(soup(self._request("get", f"{BASE_URL}/members/{username.replace('_', '-')}").text))
        self._last_comment_time = 0

    def __repr__(self):
        return f"<Client username={self.member.name} level={self.member.profile.level}>"

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
        headers = {**kwargs.pop("headers", {}), "User-Agent": random.choice(user_agent_list)}
        r = route(url, cookies=cookies, headers=headers, **kwargs)
        return self._proccess_response(r)

    def _proccess_response(self, r):
        #if we're making an ajax request we'll get a json response that we decode and check for errors
        try:
            text = r.json()
            if text.get("error", False):
                LOGGER.error(text["text"])
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
        ResultList[Thumbnail]
            List of watched things

        """
        url = f"{BASE_URL}/messages/watching/{category.name}s/page/{page}"
        html = soup(self._request("get", url).text)

        results_raw = html.find("div", class_="table").find_all("div", recursive=False)[1:]
        results = [Thumbnail(url=x.a["href"], name=x.a["title"], type=ThumbnailType[category.name], image=x.a.img["src"]) for x in results_raw]

        page, max_page = get_page_number(html)

        return ResultList(
            results=results,
            url=url,
            action=self.get_watched,
            page=page,
            max_page=max_page
        )

    def tracking(self, page):
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

    def membership(self, page):
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

    def report(self, page):
        """Report a page. This can take any object that has an id and url attribute.

        Parameters
        -----------
        page : Union[Addon, Article, BaseMetaClass, Blog, Engine, File, Game, Group, Hardware, HardwareSoftwareMetaClass, Media, Member, Mod, PageMetaClass, Platform, Poll, Software, Team]
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

    def add_comment(self, page, text, *, comment = None):
        """Add a comment to a page.

        Parameters
        -----------
        page : Union[Addon, Article, BaseMetaClass, Blog, Engine, File, Game, Group, Hardware, HardwareSoftwareMetaClass, Media, Member, Mod, PageMetaClass, Platform, Poll, Software, Team]
            Must be a moddb.page, the page you wish to add the comment to.
        test : str
            The content of the comment you wish to post
        comment : Optional[Comment] 
            If you wish to reply to another comment you must provide the comment
            object for it there.

        Returns
        --------
        Union[Addon, Article, BaseMetaClass, Blog, Engine, File, Game, Group, Hardware, HardwareSoftwareMetaClass, Media, Member, Mod, PageMetaClass, Platform, Poll, Software, Team]
            The page's updated object containing the new comment and any other new data that 
            has been posted since then
        """
        if self._last_comment_time + 60 > time.time():
            raise ModdbException("You must wait at least one minute between each comment")

        r = self._request("post", page.url,
            data = {
                "formhash": generate_hash(),
                "replyid": comment.id if comment else 0,
                "page": 1,
                "summary": text,
                "comment": "Save comment"
            }
        )

        self._last_comment_time = time.time()

        return page.__class__(soup(r.text))

    def _comment_state_update(self, comment):
        if comment is None:
            raise ModdbException("This comment no longer exists or is no longer on the page it was initially retrieved from.")

        r = self._request("post", f"{BASE_URL}/messages/ajax/action/",
            data = {
                "ajax": "t",
                "action": "delete",
                "sitearea": "comment",
                "siteareaid": comment.id,
                "hash": comment._hash
            },
            allow_redirects=False
        )

        return r

    def delete_comment(self, comment):
        """This will delete the supplied comment provided you have the correct permissions.
        This is an expensive request because if how moddb works. It needs to make two requests
        in order to get the correct hash to delete the comment. In addition, it may fail if the
        comment has changed location (page number) from what the object says. It is recommended
        to use a newly created comment object that is less than 30 minutes old.

        Parameters
        -----------
        comment : Comment
            The comment to delete

        Raises
        -------
        ModdbException
            An error occured while trying to delete the comment

        Returns
        --------
        bool
            True if the comment was successfully deleted
        """
        with self:
            page = parse(comment._url)
            updated_comment = get(page.comments, id=comment.id)

        r = self._comment_state_update(updated_comment)

        return "You have <u>deleted</u> this comment" in r.json()["text"]

    def undelete_comment(self, comment):
        """This will undelete the supplied comment provided you have the correct permissions.
        This is an expensive request because if how moddb works. It needs to make three requests
        in order to get the correct hash to undelete the comment. In addition, it may fail if the
        comment has changed location (page number) from what the object says. It is recommended
        to use a newly created comment object that is less than 30 minutes old.

        Parameters
        -----------
        comment : Comment
            The comment to undelete

        Raises
        -------
        ModdbException
            An error occured while trying to undelete the comment

        Returns
        --------
        bool
            True if the comment was successfully undeleted
        """
        with self:
            page = parse(comment._url)
            updated_comment = get(page._get_comments_from_url(comment._url, show_deleted=True), id=comment.id)

        r = self._comment_state_update(updated_comment)

        return "You have <u>authorized</u> this comment" in r.json()["text"]

    def edit_comment(self, comment, new_text):
        """Edit the contents of a comment. You can only edit your comment 120 minutes after it has 
        been posted
        
        Parameters
        -----------
        comment : Comment
            The comment to edit
        new_text : str
            The new content of the comment

        Raises
        -------
        ModdbException
            An error has occured trying to edit the comment

        Returns
        --------
        bool
            True if the comment was successfully edited        
        """
        r = self._request("post", f"{BASE_URL}/comment/ajax/post",
            data = {
                "ajax": "t",
                "id": comment.id,
                "summary": new_text
            }
        )

        return "Your comment has been saved" in r.json()["text"]

    def add_review(self, page, rating, *, text = None, has_spoilers = False):
        """Rate and review a page. If you rating is below 3 or above 8 you will be asked
        to also provide a review or else the request will not be made. This is also
        used to edit existing reviews.

        Parameters
        -----------
        page : Union[Mod, Game, Engine, Hardware, Software, Platform]
            The page you wish to review
        rating : int
            The rating from 1 to 10
        text : str
            The text review you are giving of this page
        has_spoilers : bool
            Whether or not this review contains spoilers.

        Raises
        -------
        ModdbException
            An error occured trying to review the page.

        Returns
        --------
        bool
            True of the review was successfuly submitted.

        """
        if not (2 < rating < 9) and review is None:
            raise ModdbException("Please include a review to justify such a low/high rating.") 

        with self:
            page = parse(page.url)    

        r = self._request("post", f"{BASE_URL}/reviews/ajax", 
            data={
                "ajax" : "t",
                "sitearea": page.url.split("/")[-2],
                "siteareaid": page.id,
                "hash": page._review_hash,
                "earlyaccess": int(page.profile.status == Status.early_access),
                "rating": rating,
                "summary": text,
                "spoiler": int(has_spoilers)
            },
            allow_redirects=False
        )

        return "Your rating has been saved" in r.json()["text"] 

    def delete_review(self, review):
        """Delete your review on the given page. This function will do two requests in order
        to delete your review.

        Parameters
        -----------
        review : Review
            The review you wish to delete

        Raises
        -------
        ModdbException
            An error occured while trying to delete the review

        Returns
        --------
        bool
            True if the review was successfully deleted
        """
        with self:
            hash_review = self.member.get_reviews()[0]

        r = self._request("post", f"{BASE_URL}/messages/ajax/action/",
            data={
                "ajax": "t",
                "action": "delete",
                "sitearea": "reviews",
                "siteareaid": review.id,
                "hash": hash_review._hash,
                "ispd": 1
            },
            allow_redirects = False
        )

        return "You have <u>deleted</u> this review." in r.json()["text"]
