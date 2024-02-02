from __future__ import annotations
import logging

from typing import TYPE_CHECKING, List, Tuple

from ..boxes import (
    MemberProfile,
    MemberStatistics,
    PartialTag,
    Profile,
    ResultList,
    Statistics,
    Thumbnail,
    _parse_results,
)
from ..enums import GroupCategory, Membership, SearchCategory, ThumbnailType, TimeFrame
from ..utils import LOGGER, concat_docs, get_page, join
from .article import Blog
from .base import BaseMetaClass, PageMetaClass
from .mixins import GetAddonsMixin, GetEnginesMixin, GetGamesMixin, GetModsMixin, GetWaresMixin

if TYPE_CHECKING:
    import bs4

    from ..boxes import CommentList


@concat_docs
class Group(PageMetaClass, GetAddonsMixin):
    """This object represents the group model of  Certain attributes can be None if the group
    has been set to private. If you wish to see a group you have access to then you can login with the
    login

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
    subscriptions : :class:`.Membership`
        The subscription system of the group (private, invitation)
    category : :class:`.GroupCategory`
        The category of the group (funny, literature)

    Sorting
    --------
        * **id** - order group by date, asc is most recent first, desc is oldest first
        * **ranktoday** - order by daily ranking, asc is highest ranked, desc is lowest rank
        * **visitstotal** - order by most views, asc is highest views, desc is lowest views
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **membercount** - order by number of members, asc is most members first, desc is lest member first

    Attributes
    -----------
    name : str
        The name of the group
    private : bool
        Whether or not the group is private
    profile : Profile
        The profile object for the group
    stats : Statistics
        The stats of the Group
    tags : List[PartialTag]
        A list of partial tags. You can use `get_tags` and then use the name id to get the right one.
    embed : str
        The html for athe group embed
    medias : List[Thumbnail]
        A list of media like thumbnail objects representing all the images, videos and audio
        clips that a group has published.
    suggestions : List[Thumbnail]
        A list of group like thumbnail objects representing the suggestions made by moddb to
        members visiting this group
    articles : List[Thumbnail]
        A list of article like thumbnail objects representing some of the articles published
        by the group
    description : str
        The plaintext description of the group
    """

    get_reviews = None

    def __init__(self, html: bs4.BeautifulSoup):
        self.name = html.find("div", class_="title").h2.a.string
        BaseMetaClass.__init__(self, html)
        self.private = False

        try:
            self.profile = Profile(html)
        except AttributeError:
            LOGGER.info(
                "Entity '%s' has no profile (private)",
                self.name,
                exc_info=LOGGER.level >= logging.DEBUG,
            )
            self.profile = None
            self.private = True

        try:
            self.stats = Statistics(html)
        except AttributeError:
            LOGGER.info(
                "Entity '%s' has no stats (private)",
                self.name,
                exc_info=LOGGER.level >= logging.DEBUG,
            )
            self.stats = None

        try:
            raw_tags = html.find("form", attrs={"name": "tagsform"}).find_all("a")
            self.tags = [
                PartialTag(x.string, join(x["href"]), x["href"].split("/")[-1])
                for x in raw_tags
                if x.string is not None
            ]
        except AttributeError:
            LOGGER.info(
                "Entity '%s' has no tags (private)",
                self.name,
                exc_info=LOGGER.level >= logging.DEBUG,
            )
            self.tags = []

        try:
            self.embed = html.find("input", type="text", class_="text textembed")["value"]
        except TypeError:
            try:
                self.embed = str(html.find_all("textarea")[1].a)
            except IndexError:
                LOGGER.info(
                    "Group '%s' has no embed", self.name, exc_info=LOGGER.level >= logging.DEBUG
                )
                self.embed = None

        self.suggestions = self._get_suggestions(html)

        try:
            articles_raw = html.find("span", string="Articles").parent.parent.parent.find(
                "div", class_="table"
            )
            thumbnails = articles_raw.find_all(
                "div", class_="row rowcontent clear", recursive=False
            )
            self.articles = [
                Thumbnail(
                    name=x.a["title"],
                    url=x.a["href"],
                    image=x.a.img["src"],
                    summary=x.find("p").string,
                    date=x.find("time")["datetime"],
                    type=ThumbnailType.article,
                )
                for x in thumbnails
            ]
        except AttributeError:
            LOGGER.info(
                "Group '%s' has no article suggestions",
                self.name,
                exc_info=LOGGER.level >= logging.DEBUG,
            )
            self.articles = []

        try:
            self.description = html.find("div", id="profiledescription").text
        except AttributeError:
            self.description = (
                html.find("div", class_=["column", "span-all"])
                .find("div", class_="tooltip")
                .parent.text
            )

        self.medias = self._get_media(2, html=html)

    def _get_suggestions(self, html: bs4.BeautifulSoup) -> List[Thumbnail]:
        """Hidden method used to get the list of suggestions on the page. As with most things, this list of suggestions
        will be a list of Thumbnail objects that can be parsed individually. Slightly modified to fit a group

        Parameters
        -----------
        html : bs4.BeautifulSoup
            The html page we are trying to parse the suggestions for

        Returns
        --------
        List[Thumbnail]
            The list of suggestions as thumbnails.
        """
        try:
            suggestions_raw = (
                html.find("span", string=("You may also like", "Popular Articles"))
                .parent.parent.parent.find("div", class_="table")
                .find_all("div", recursive=False)
            )
        except AttributeError:
            LOGGER.info(
                "Group '%s' has no sidebar suggestions",
                self.name,
                exc_info=LOGGER.level >= logging.DEBUG,
            )
            return []

        suggestions = []
        for x in suggestions_raw:
            try:
                link = x.find("a", class_="image")
                suggestion_type = link["href"].split("/")[1].replace("s", "")
                suggestion = Thumbnail(
                    name=link["title"],
                    url=link["href"],
                    image=link.img["src"],
                    type=ThumbnailType[suggestion_type],
                )
                suggestions.append(suggestion)
            except (AttributeError, TypeError):
                pass

        return suggestions

    def __repr__(self):
        return f"<Group name={self.name}>"


@concat_docs
class Team(Group, GetEnginesMixin, GetGamesMixin, GetModsMixin, GetWaresMixin):
    """A team is a group of people, which are the author of a game, a mod or an engine. A group has members which all
    have rights on those page. Like a member but instead of a single person authoring various mods and games it's several.

    Parameters
    ------------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
    subscriptions : :class:`.Membership`
        The subscription system of the company (private, invitation)
    category : :class:`.TeamCategory`
        What does the team do (publisher, developer)

    Sorting
    --------
        * **id** - order by creation, desc is most recent first, asc is oldest first
        * **ranktoday** - order by daily ranking, asc is highest ranked, desc is lowest rank
        * **visitstotal** - order by most views, asc is highest views, desc is lowest views
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **game** - order by game???
        * **dateup** - order by latest update, asc is most recent update first, desc is oldest update first

    Attributes
    -----------
    games : List[Thumbnail]
        A list of game like thumbnails that the team has authored.
    engines : List[Thumbnail]
        A list of engine like objects that the team has authored.

    """

    def __init__(self, html: bs4.BeautifulSoup):
        super().__init__(html)
        try:
            self.games = self._get_games(html)
        except AttributeError:
            LOGGER.info("Team '%s' has no games", self.name, exc_info=LOGGER.level >= logging.DEBUG)
            self.games = []

        try:
            self.engines = self._get_engines(html)
        except AttributeError:
            LOGGER.info(
                "Team '%s' has no engines", self.name, exc_info=LOGGER.level >= logging.DEBUG
            )
            self.engines = []
        try:
            mods = (
                html.find("span", string="Popular Mods")
                .parent.parent.parent.find("div", class_="table")
                .find_all("div", recursive=False)[1:]
            )
            self.mods = [
                Thumbnail(
                    name=x.a["title"],
                    url=x.a["href"],
                    type=ThumbnailType.mod,
                    image=x.a.img["src"],
                )
                for x in mods
            ]
        except AttributeError:
            LOGGER.info("Team '%s' has no mods", self.name, exc_info=LOGGER.level >= logging.DEBUG)
            self.mods = []


@concat_docs
class Member(PageMetaClass, GetGamesMixin, GetModsMixin, GetAddonsMixin):
    """The object to represent an individual member on ModDB

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Sorting
    --------
    * **username** - sort alphabetically by username, asc is z-a and desc is a-z
    * **id** - sort by member creation date, asc is most recent, desc is oldest
    * **online** - sort by last online, asc is most recently seen online and desc is least recently

    Attributes
    -----------
    profile : MemberProfile
        Since member profile boxes have no overlap with other profiles, they are a separate object type
        but serve the same function of making the side box "Profile" into an object, except exclusively
        for a member page.
    stats : MemberStatistics
        Since member statistics have no overlap with regular statistic pages, they are a separate object type
        but serve the same function of making the side box "Statistics" into an object, but exclusively for
        the member page.
    description : str
        Description written on the member profile
    groups : List[Thumbnail]
        A list of group/team like thumbnail objects representing both the Teams the member is part of and the
        Groups the member is part of.
    blog : Blog
        The front page blog shown on the member page
    blogs : List[Thumbnail]
        A list of blog like thumbnails representing the blog suggestion of a member's frontpage
    friends : List[Thumnails]
        A list of member like thumbnails representing some of the friends shown on the member's front
        page
    """

    def __init__(self, html: bs4.BeautifulSoup):
        super().__init__(html, SearchCategory.members)
        try:
            self.profile = MemberProfile(html)
        except AttributeError:
            LOGGER.info(
                "Member '%s' has no profile (private)",
                self.name,
                exc_info=LOGGER.level >= logging.DEBUG,
            )
            self.profile = None

        try:
            self.stats = MemberStatistics(html)
        except AttributeError:
            LOGGER.info(
                "Member '%s' has no stats (private)",
                self.name,
                exc_info=LOGGER.level >= logging.DEBUG,
            )
            self.stats = None

        try:
            self.description = html.find("div", id="profiledescription").p.string
        except AttributeError:
            LOGGER.info(
                "Member '%s' has no description", self.name, exc_info=LOGGER.level >= logging.DEBUG
            )
            self.description = None

        try:
            groups_raw = (
                html.find("span", string="Groups")
                .parent.parent.parent.find("div", class_="table")
                .find_all("div", recursive=False)[:-2]
            )
            self.groups = [
                Thumbnail(name=div.a["title"], url=div.a["href"], type=ThumbnailType.group)
                for div in groups_raw
            ]
        except AttributeError:
            LOGGER.info(
                "Member '%s' doesn't have any groups",
                self.name,
                exc_info=LOGGER.level >= logging.DEBUG,
            )
            self.groups = []

        try:
            blogs_raw = (
                html.find("span", string="My Blogs")
                .parent.parent.parent.find("div", class_="table")
                .find_all("div", recursive=False)
            )
            self.blog = Blog(heading=blogs_raw.pop(0), text=blogs_raw.pop(0))
        except (TypeError, AttributeError):
            self.blog = None
            LOGGER.info(
                "Member '%s' has no front page blog",
                self.name,
                exc_info=LOGGER.level >= logging.DEBUG,
            )

        try:
            blogs_raw = (
                html.find("span", string="My Blogs")
                .parent.parent.parent.find("div", class_="table")
                .find_all("div", recursive=False)
            )
            self.blogs = [
                Thumbnail(name=blog.a.string, url=blog.a["href"], type=ThumbnailType.blog)
                for blog in blogs_raw[:-2]
            ]
        except (TypeError, AttributeError):
            self.blogs = []
            LOGGER.info(
                "Member '%s' has no blog suggestions",
                self.name,
                exc_info=LOGGER.level >= logging.DEBUG,
            )

        try:
            friends = html.find("div", class_="table tablerelated").find_all(
                "div", recursive=False
            )[1:]
            self.friends = [
                Thumbnail(
                    name=friend.a["title"],
                    url=friend.a["href"],
                    type=ThumbnailType.member,
                )
                for friend in friends
            ]
        except AttributeError:
            self.friends = []
            LOGGER.info(
                "Member '%s' has no friends ;(", self.name, exc_info=LOGGER.level >= logging.DEBUG
            )

    def __repr__(self):
        return f"<Member name={self.name} level={self.profile.level}>"

    def get_blogs(
        self,
        index: int = 1,
        *,
        query: str = None,
        timeframe: TimeFrame = None,
        sort: Tuple[str, str] = None,
    ) -> ResultList:
        """Search through a member's blogs one page at a time with certain filters.

        Parameters
        -----------
        index : int
            The page index you wish to get the blogs for, allows to hop around.
        timeframe : TimeFrame
            The date the blog was added, optional
        query : str
            The string to look for in the blog title, optional.
        sort : Tuple[str, str]
            The sorting tuple to sort by

        Returns
        --------
        ResultList[Blog]
            The list of blogs on this page.
        """
        params = {
            "filter": "t",
            "kw": query,
            "timeframe": timeframe.value if timeframe else None,
            "sort": f"{sort[0]}-{sort[1]}" if sort else None,
        }

        url = f"{self.url}/blogs"
        html = get_page(f"{url}/page/{index}", params=params)
        results, current_page, total_pages, total_results = _parse_results(html)

        return ResultList(
            results=results,
            params=params,
            url=url,
            current_page=current_page,
            total_pages=total_pages,
            total_results=total_results,
        )

    def get_member_comments(self, index: int = 1, *, show_deleted: bool = False) -> CommentList:
        """Gets a page of all the comments a member has posted.

        Parameters
        -----------
        index : int
            The page number to get the comments from.
        show_deleted : Optional[bool]
            Pass true to show deleted user comments. Only works if it is a page
            you have permissions on.

        Returns
        --------
        CommentList[Comment]
            A list of the comments made by the user.

        """
        params = {"deleted": "t" if show_deleted else None}

        html = get_page(f"{self.url}/comments/page/{index}", params=params)
        return self._get_comments(html)

    def get_friends(self, index: int = 1, *, username: str = None) -> ResultList:
        """Get a page of the friends of the member

        Parameters
        -----------
        index : int
            The page number to get the friends from.
        username : Optional[str]
            The username of the user you are looking for

        Returns
        --------
        ResultList[Thumbnail]
            A list of member like thumbnails of the member's friends
        """
        params = {"filter": "t", "username": username}

        return self._get(f"{self.url}/friends/page/{index}", params=params)

    def get_groups(
        self,
        index: int = 1,
        *,
        query: str = None,
        subscription: Membership = None,
        category: GroupCategory = None,
    ) -> ResultList:
        """Get a page of the groups and teams a member is part of.

        Parameters
        -----------
        index : int
            The page number to get the friends from.
        query : Optional[str]
            The text to look for in the group's name
        subscription : Optional[Membership]
            The membership rules
        category : Optional[GroupCategory]
            The category of groups to search for

        Returns
        --------
        ResultList[Thumbnail]
            A list of team/group like thumbnails the member is part of
        """
        params = {
            "filter": "t",
            "kw": query,
            "subscription": subscription.value if subscription else None,
            "category": category.value if category else None,
        }

        return self._get(f"{self.url}/groups/page/{index}", params=params)
