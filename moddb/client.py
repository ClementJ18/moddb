from __future__ import annotations

import random
import re
import sys
from typing import TYPE_CHECKING, Any, List, Tuple, Union

import requests
from bs4 import BeautifulSoup
from requests import utils

from .base import parse_page
from .boxes import ResultList, Thumbnail, _parse_results
from .enums import Status, ThumbnailType
from .errors import ModdbException
from .pages import Member
from .utils import (
    BASE_URL,
    COMMENT_LIMITER,
    LOGGER,
    concat_docs,
    generate_hash,
    generate_login_cookies,
    get,
    get_date,
    get_page_type,
    get_sitearea,
    get_siteareaid,
    join,
    raise_for_status,
    ratelimit,
    soup,
    user_agent_list,
)

if TYPE_CHECKING:
    from .boxes import Comment, Tag
    from .enums import WatchType
    from .pages import Engine, Game, Group, Mod, Review, Team


class Message:
    """A single message within a thread.

    Attributes
    -----------
    id : int
        The id of the message
    member : Thumbnail
        A member type thumbnail representing the member
        who sent the message
    timestamp : datetime.datetime
        Message send date
    text : str
        The html text of the message
    """

    def __init__(self, html: BeautifulSoup):
        member = html.find("a", class_="avatar")

        self.id = int(html["id"])
        self.member = Thumbnail(url=member["href"], type=ThumbnailType.member, name=member["title"])
        self.timestamp = get_date(html.find("time")["datetime"])
        self.text = html.find("div", class_="comment").text

    def __repr__(self):
        return f"< Message member={self.member} >"


class Thread:
    """A thread is a conversation between two or more members in which
    one or more messages can be sent.

    Sorting
    --------
        * **id** - when the message was sent, asc is oldest, desc is most recent
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **hasread** - order by whether or the message has been read, asc is unread first, desc is read first
        * **hasreplied** - order by whether or not you have replied to the message, asc us unreplied first, desc is replied first

    Attributes
    -----------
    name : str
        Name of the thread
    id : int
        Id of the thread
    count : int
        The number of messages in this thread
    members : List[Tumbnail]
        All the members participating in the thread. Note: The
        thumbnail of the member who fetched the message will always
        be first and will have their name attribute be 'you' instead
        of the username
    message : List[Message]
        The messages associated to this thread
    """

    def __init__(self, html: BeautifulSoup):
        thread = html.find("div", id="firstmessage")
        header = thread.find("div", class_="normalcorner")

        header_string = header.find("span", class_="heading").string
        header_match = re.match(r"(.*) \(([0-9]*) messages?\)", header_string)
        if header_match is None:
            self.name = header_string
            self.count = 1
        else:
            self.name = header_match.group(1)
            self.count = int(header_match.group(2))

        members = thread.find("p", class_="introduction").strong.find_all("a")
        option = header.find("a", class_=["deleteicon"])
        messages = thread.find("div", class_=["tablecomments"]).find_all("div", recursive=False)

        self.id = int(option["href"][option["href"].index("=") + 1 :])
        self.members = [
            Thumbnail(url=member["href"], name=member.string, type=ThumbnailType.member)
            for member in members
        ]
        self.messages = [Message(message) for message in messages]

    def __repr__(self):
        return f"< Thread name={self.name} count={self.count} >"


class ThreadThumbnail:
    """The thumbnail of a thread, these represent partial objects that
    must be parsed using a client to get the full thread.

    Attributes
    -----------
    name : str
        The name of the thread
    id : int
        The id of the thread
    url : str
        The url for the thread
    last_messager : Thumbnail
        A thumbnail representig the user that sent the
        last message
    timestamp : datetime.datetime
        Datetime of the last message
    content : str
        Content of the last message. Useful for checking
        the last message without having to parse the thread.
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.url = join(kwargs.get("url"))
        self.last_messager = kwargs.get("last_messager")
        self.timestamp = kwargs.get("timestamp")
        self.content = kwargs.get("content")
        self.id = int(self.url.split("/")[-1])

    def __repr__(self):
        return f"< ThreadThumbnail name={self.name} last_messager={self.last_messager} >"


@concat_docs
class Update(Thumbnail):
    """An update object. Which is basically just a fancy thumbnail with a couple extra attributes and
    methods.

    Attributes
    -----------
    updates : List[Thumbnail]
        A list of thumbnail objects of the things thave have been posted (new files, new images)
    """

    def __init__(self, **attrs):
        super().__init__(**attrs)

        self.updates = attrs.get("updates")
        self._unfollow_url = join(attrs.get("unfollow"))
        self._clear_url = join(attrs.get("clear"))
        self._client = attrs.get("client")

    def __repr__(self):
        return f"<Update name={self.name} type={self.type.name} updates={len(self.updates)}>"

    def clear(self) -> bool:
        """Clears all updates

        Raises
        -------
        ModdbException
            An error has occured while trying to clear the updates for this page

        Returns
        --------
        bool
            True if the updates were successfully cleared
        """
        r = self._client._request("POST", self._clear_url, data={"ajax": "t"})

        return "successfully removed" in r.json()["text"]

    def unfollow(self) -> bool:
        """Unfollows the page. This will also clear the updates

        Raises
        -------
        ModdbException
            An error has occured while trying to unfollow this page

        Returns
        --------
        bool
            True if the page was successfully unfollowed
        """
        r = self._client._request("POST", self._unfollow_url, data={"ajax": "t"})

        return "no longer watching" in r.json()["text"]


@concat_docs
class Request(Thumbnail):
    """A thumbnail with two extra methods used to clear and accept requests.

    Attributes
    -----------
    """

    def __init__(self, **attrs):
        super().__init__(**attrs)

        self._decline = join(attrs.get("decline"))
        self._accept = join(attrs.get("accept"))
        self._client = attrs.get("client")

    def accept(self) -> bool:
        """Accept the friend request.

        Raises
        -------
        ModdbException
            An error has occured while trying to accept the request

        Returns
        --------
        bool
            True if the request was successfully accepted
        """
        r = self._client._request("POST", self._accept, data={"ajax": "t"})

        return "now friends with" in r.json()["text"]

    def decline(self) -> bool:
        """Decline the friend request

        Raises
        -------
        ModdbException
            An error has occured while trying to decline the request

        Returns
        --------
        bool
            True if the page was successfully declined
        """
        r = self._client._request("POST", self._decline, data={"ajax": "t"})

        return "successfully removed" in r.json()["text"]

    def __repr__(self):
        return f"<Request from={self.name}>"


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

    def __init__(self, username: str, password: str):
        session = requests.Session()
        session.cookies = generate_login_cookies(username, password, session=session)
        self._session = session
        LOGGER.info("Login successful for %s", username)

        self.member = Member(
            soup(self._request("GET", f"{BASE_URL}/members/{username.replace('_', '-')}").text)
        )

    def __repr__(self):
        return f"<Client username={self.member.name} level={self.member.profile.level}>"

    def __enter__(self):
        self._fake_session = sys.modules["moddb"].SESSION
        sys.modules["moddb"].SESSION = self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.modules["moddb"].SESSION = self._fake_session
        delattr(self, "_fake_session")

    @ratelimit
    def _request(self, method, url, **kwargs):
        """Making sure we do our request with the cookies from this client rather than the cookies
        of the library."""
        cookies = utils.dict_from_cookiejar(self._session.cookies)
        headers = {
            **kwargs.pop("headers", {}),
            "User-Agent": random.choice(user_agent_list),
        }

        req = requests.Request(
            method, url, headers=headers, cookies=cookies, data=kwargs.pop("data", {})
        )
        prepped = self._session.prepare_request(req)
        LOGGER.info("Request: %s", prepped.url)

        r = self._session.send(prepped, allow_redirects=kwargs.pop("allow_redirects", True))
        raise_for_status(r)

        return r

    def get_updates(self) -> List[Update]:
        """Get the current updates the user has for models they are subscribed to.

        Returns
        --------
        List[Update]
            List of updates (thumbnail like objects with extra methods and an extra attribute)
        """
        r = self._request("GET", f"{BASE_URL}/messages/updates")
        html = soup(r.text)
        updates = []

        strings = (
            "Mods Watch",
            "Members Watch",
            "Engines Watch",
            "Groups Watch",
            "Games Watch",
        )
        raw = html.find_all("span", string=strings)
        objects = [
            e.parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)
            for e in raw
        ]

        objects_raw = [item for sublist in objects for item in sublist[:-1]]
        for update in objects_raw:
            thumbnail = update.find("a")
            unfollow = update.find("a", title="Stop Watching")["href"]
            clear = update.find("a", title="Clear")["href"]
            updates_raw = update.find("p").find_all("a")

            updates.append(
                Update(
                    name=thumbnail["title"],
                    url=thumbnail["href"],
                    type=get_page_type(thumbnail["href"]),
                    image=thumbnail.img["src"],
                    client=self,
                    unfollow=unfollow,
                    clear=clear,
                    updates=[
                        Thumbnail(name=x.string, url=x["href"], type=get_page_type(x["href"]))
                        for x in updates_raw
                    ],
                    date=get_date(update.find("time")["datetime"]),
                )
            )

        return updates

    def clear_updates(self, category: WatchType) -> bool:
        """Clear all updates for a specific category of
        watched. This method will conduct two requests because
        the clear update request requires a hash generated by
        moddb.

        Parameters
        -----------
        category: WatchType
            The category of watched to clear

        Returns
        --------
        bool
            Whether or not the clear was successful
        """
        hash_page = self._request("GET", f"{BASE_URL}/messages/updates")
        html = soup(hash_page.text)
        pattern = re.compile(rf".*\/clearall\/(.*)\/1\/{category.name}s")
        link = html.find("a", href=pattern)
        if link is None:
            return True

        r = self._request("POST", f'{BASE_URL}{link["href"]}', data={"ajax": "t"})

        return "updates were cleared" in r.json()["text"]

    def get_friend_requests(self) -> List[Request]:
        """Get the current friend requests the user has.

        Returns
        --------
        List[Request]
            List of requests (thumbnail like objects with extra methods)
        """
        r = self._request("GET", f"{BASE_URL}/messages/updates")
        html = soup(r.text)
        requests = []
        raw = html.find("span", string="Friend Requests")
        raw_requests = raw.parent.parent.parent.find("div", class_="table").find_all(
            "div", recursive=False
        )

        for request in raw_requests[:-1]:
            thumbnail = request.find("a")
            accept = request.find("a", title="Accept")["href"]
            decline = request.find("a", title="Decline")["href"]

            requests.append(
                Request(
                    name=thumbnail["title"],
                    url=thumbnail["href"],
                    type=get_page_type(thumbnail["href"]),
                    image=thumbnail.img["src"],
                    client=self,
                    accept=accept,
                    decline=decline,
                    date=get_date(request.find("time")["datetime"]),
                )
            )

        return requests

    def get_watched(self, category: WatchType, page: int = 1) -> ResultList:
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
        url = f"{BASE_URL}/messages/watching/{category.name}s"
        html = soup(self._request("GET", f"{url}/page/{page}").text)
        results, current_page, total_pages, total_results = _parse_results(html)

        return ResultList(
            results=results,
            url=url,
            current_page=current_page,
            total_pages=total_pages,
            total_results=total_results,
        )

    def tracking(self, page: Union[Mod, Game, Engine, Group, Member]) -> bool:
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
        r = self._request(
            "POST",
            f"{BASE_URL}/messages/ajax/action/",
            data={
                "ajax": "t",
                "action": "watch",
                "sitearea": get_sitearea(page.url),
                "siteareaid": page.id,
            },
            allow_redirects=False,
        )

        return "be notified" in r.json()["text"]

    def like_comment(self, comment: Comment) -> bool:
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
        r = self._request(
            "POST",
            f"{BASE_URL}/messages/ajax/action/",
            data={
                "ajax": "t",
                "action": "karmagood",
                "sitearea": "comment",
                "siteareaid": comment.id,
            },
            allow_redirects=False,
        )

        return "successfully issued" in r.json()["text"]

    def dislike_comment(self, comment: Comment) -> bool:
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

        r = self._request(
            "POST",
            f"{BASE_URL}/messages/ajax/action/",
            data={
                "ajax": "t",
                "action": "karmabad",
                "sitearea": "comment",
                "siteareaid": comment.id,
            },
            allow_redirects=False,
        )

        return "successfully issued" in r.json()["text"]

    def membership(self, page: Union[Group, Team]) -> bool:
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
        r = self._request(
            "POST",
            f"{BASE_URL}/groups/ajax/members/change/{page.id}",
            data={"ajax": "t"},
            allow_redirects=False,
        )

        return "successfully joined" in r.json()["text"]

    def report(self, page: Any) -> bool:
        """Report a page. This can take any object that has an id and url attribute.

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
        r = self._request(
            "POST",
            f"{BASE_URL}/messages/ajax/action/",
            data={
                "ajax": "t",
                "action": "report",
                "sitearea": get_sitearea(page.url),
                "siteareaid": page.id,
            },
            allow_redirects=False,
        )

        return "already reported this content" not in r.json()["text"]

    def unfriend(self, member: Member) -> bool:
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
        r = self._request(
            "POST",
            f"{BASE_URL}/members/ajax/friends/delete/{member.id}",
            data={"ajax": "t"},
            allow_redirects=False,
        )

        return "no longer friends with this member" in r.json()["text"]

    def send_request(self, member: Member) -> bool:
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
        r = self._request(
            "POST",
            f"{BASE_URL}/members/ajax/friends/add/{member.id}",
            data={"ajax": "t"},
            allow_redirects=False,
        )

        return "friend request has been sent" in r.json()["text"]

    def add_comment(self, page: Any, text: str, *, comment: Comment = None) -> Any:
        """Add a comment to a page.

        Parameters
        -----------
        page : Any
            Must be a moddb.page, the page you wish to add the comment to.
        test : str
            The content of the comment you wish to post
        comment : Optional[Comment]
            If you wish to reply to another comment you must provide the comment
            object for it there.

        Returns
        --------
        Any
            The page's updated object containing the new comment and any other new data that
            has been posted since then
        """
        COMMENT_LIMITER.try_acquire(self.member.name_id)
        r = self._request(
            "POST",
            page.url,
            data={
                "formhash": generate_hash(),
                "replyid": comment.id if comment else 0,
                "page": 1,
                "summary": text,
                "comment": "Save comment",
            },
        )

        return page.__class__(soup(r.text))

    def _comment_state_update(self, comment):
        if comment is None:
            raise ModdbException(
                "This comment no longer exists or is no longer on the page it was initially retrieved from."
            )

        r = self._request(
            "POST",
            f"{BASE_URL}/messages/ajax/action/",
            data={
                "ajax": "t",
                "action": "delete",
                "sitearea": "comment",
                "siteareaid": comment.id,
                "hash": comment._hash,
            },
            allow_redirects=False,
        )

        return r

    def delete_comment(self, comment: Comment) -> bool:
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
            page = parse_page(comment._url)
            updated_comment = get(page.comments, id=comment.id)

        r = self._comment_state_update(updated_comment)

        return "You have <u>deleted</u> this comment" in r.json()["text"]

    def undelete_comment(self, comment: Comment) -> bool:
        """This will undelete the supplied comment provided you have the correct permissions.
        This is an expensive request because of how moddb works. It needs to make three requests
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
            page = parse_page(comment._url)
            updated_comment = get(
                page._get_comments_from_url(comment._url, show_deleted=True),
                id=comment.id,
            )

        r = self._comment_state_update(updated_comment)

        return "You have <u>authorized</u> this comment" in r.json()["text"]

    def edit_comment(self, comment: Comment, new_text: str) -> bool:
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
        r = self._request(
            "POST",
            f"{BASE_URL}/comment/ajax/post",
            data={"ajax": "t", "id": comment.id, "summary": new_text},
        )

        return "Your comment has been saved" in r.json()["text"]

    def add_review(
        self, page: Any, rating: int, *, text: str = None, has_spoilers: bool = False
    ) -> bool:
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
        if not (2 < rating < 9) and text is None:
            raise ModdbException("Please include a review to justify such a low/high rating.")

        with self:
            page = parse_page(page.url)

        r = self._request(
            "POST",
            f"{BASE_URL}/reviews/ajax",
            data={
                "ajax": "t",
                "sitearea": get_sitearea(page.url),
                "siteareaid": page.id,
                "hash": page._review_hash,
                "earlyaccess": int(page.profile.status == Status.early_access),
                "rating": rating,
                "summary": text,
                "spoiler": int(has_spoilers),
            },
            allow_redirects=False,
        )

        return "Your rating has been saved" in r.json()["text"]

    def delete_review(self, review: Review) -> bool:
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

        r = self._request(
            "POST",
            f"{BASE_URL}/messages/ajax/action/",
            data={
                "ajax": "t",
                "action": "delete",
                "sitearea": "reviews",
                "siteareaid": review.id,
                "hash": hash_review._hash,
                "ispd": 1,
            },
            allow_redirects=False,
        )

        return "You have <u>deleted</u> this review." in r.json()["text"]

    def get_threads(
        self,
        query: str = None,
        read: bool = None,
        replied: bool = None,
        sent_items: bool = False,
        sort: Tuple[str, str] = None,
    ) -> List[ThreadThumbnail]:
        """Get all the messages this user has sent or received. This does not return threads you
        have left.

        Parameters
        -----------
        query : Optional[str]
            Optional query to filter messages
        read : Optional[bool]
            True to filter only read message, false to filter unread, None to allow both
        replied : Optional[bool]
            True to filter messages where you are the last message, False for messages
            where another user is the last message, None for both.
        sent_items:
            Get only the threads you have started
        sort : Tuple[str, str]
            Optional sort tuple to order threads

        Returns
        --------
        List[ThreadThumbnail]
            Thread typed thumbnails
        """
        if sent_items:
            url = f"{BASE_URL}/messages/sentitems"
        else:
            url = f"{BASE_URL}/messages/inbox"

        r = self._request(
            "GET",
            url,
            params={
                "filter": "t",
                "kw": query,
                "hasread": int(read) if read is not None else read,
                "hasreplied": int(replied) if replied is not None else replied,
                "sort": f"{sort[0]}-{sort[1]}" if sort is not None else sort,
            },
        )
        html = soup(r.text)

        threads_raw = html.find_all("div", class_=["tabinbox"])[-1].find_all(
            "div", class_=["rowcontent"]
        )
        threads = []
        for thread in threads_raw:
            member = thread.find("span", class_="subheading").find_all("a")[0]
            threads.append(
                ThreadThumbnail(
                    url=thread.a["href"],
                    name=thread.a["title"],
                    last_messager=Thumbnail(
                        type=ThumbnailType.member, name=member.string, url=member["href"]
                    ),
                    timestamp=get_date(thread.find("time")["datetime"]),
                    content=thread.find("div", class_="content").find("p").string,
                )
            )

        return threads

    def parse_thread(self, thread: ThreadThumbnail) -> Thread:
        """Parse a thread thumbnail into a full thread object.

        Parameters
        ----------
        thread : ThreadThumbnail
            The thumbnail to parse

        Returns
        --------
        Thread
            The parsed thread and its messages
        """
        r = self._request("GET", thread.url)

        return Thread(soup(r.text))

    def send_message(self, members: List[Member], name: str, message: str) -> Thread:
        """Send a message and start a thread with one or more members

        Parameters
        ----------
        member : List[Member]
            The members to send the message to and start the
            thread with
        name : str
            The subject of the message
        message : str
            The message to send

        Returns
        --------
        Thread
            The thread started from sending this message
        """
        r = self._request(
            "POST",
            f"{BASE_URL}/messages/compose/",
            data={
                "formhash": generate_hash(),
                "membersto": ",".join(member.name for member in members),
                "name": name,
                "description": message,
                "messages": "Send+message",
            },
        )

        return Thread(soup(r.text))

    def reply_to_thread(self, thread: Union[Thread, ThreadThumbnail], text: str) -> Thread:
        """Add an additional message to an exiting thread

        Parameters
        -----------
        thread : Union[Thread, ThreadThumbnail]
            The thread to add the message to
        text : str
            The text to send

        Returns
        --------
        Thread
            The updated thread containing the new message. It is
            recommended to use this object as it also contains
            a new hash for sending another message
        """
        r = self._request(
            "POST",
            f"{BASE_URL}/messages/inbox/{thread.id}",
            data={"formhash": generate_hash(), "description": text, "messages": "Send+message"},
        )

        return Thread(soup(r.text))

    def add_member_to_thread(self, thread: Union[Thread, ThreadThumbnail], member: Member) -> bool:
        """Add a member to a conversation

        Parameters
        -----------
        thread : Union[Thread, ThreadThumbnail]
            The thread to add add a member to
        member : Member
            The member to add

        Returns
        --------
        bool
            Whether adding the member was succesful. This
            will not update the thread.
        """
        r = self._request(
            "POST",
            f"{BASE_URL}/messages/ajax/members/invite/{thread.id}",
            data={"ajax": "t", "username": member.name, "member": "0"},
            allow_redirects=False,
        )

        return "has been successfully added" in r.json()["text"]

    def leave_thread(self, thread: Union[Thread, ThreadThumbnail]) -> bool:
        """Leave a thread, you will not get any more notifications on this thread.

        Parameters
        ----------
        thread : Union[Thread, ThreadThumbnail]
            The thread to leave

        Returns
        --------
        bool
            Whether leaving the thread was successful
        """
        r = self._request(
            "POST",
            f"{BASE_URL}/messages/ajax/delete/",
            data={"ajax": "t", "thread": thread.id},
            allow_redirects=False,
        )

        return "You have successfully deleted the requested thread" in r.json()["text"]

    def mark_all_read(self) -> bool:
        """Mark all threads as read.

        Returns
        --------
        bool
            True if all threads have been marked as read
        """
        r = self._request("POST", f"{BASE_URL}/messages/ajax/markallread", data={"ajax": "t"})

        return "All messages marked as read" in r.json()["text"]

    def _vote_tag(self, tag: Tag, negative: int):
        params = {
            "ajax": "t",
            "tag": tag.name_id,
            "sitearea": get_siteareaid(tag.sitearea),
            "siteareadid": tag.siteareaid,
            "hash": generate_hash(),
            "negative": str(negative),
        }

        resp = self._request("POST", f"{BASE_URL}/tags/ajax/add", data=params)
        return resp.json()["success"]

    def upvote_tag(self, tag: Tag) -> bool:
        """Upvote a tag

        Parameters
        -----------
        tag : Tag
            The tag to upvote

        Returns
        --------
        bool
            Whether the upvote was successful
        """
        return self._vote_tag(tag, 0)

    def downvote_tag(self, tag: Tag) -> bool:
        """Downvote a tag

        Parameters
        -----------
        tag : Tag
            The tag to downvote

        Returns
        --------
        bool
            Whether the downvote was successful
        """
        return self._vote_tag(tag, 1)
