from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..boxes import PlatformStatistics, Thumbnail
from ..enums import ThumbnailType
from ..utils import LOGGER, concat_docs, get_date, join
from .base import BaseMetaClass
from .mixins import GetEnginesMixin, GetGamesMixin, GetModsMixin, GetWaresMixin

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


@concat_docs
class Platform(
    BaseMetaClass,
    GetModsMixin,
    GetGamesMixin,
    GetEnginesMixin,
    GetWaresMixin,
):
    """Represents the platform supporting the game/engines. Game and engines may have mutiple platforms.

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
    released : :class:`.Status`
        Current status of release (unreleased, early access, ect...)

    Sorting
    --------
        * **released** - when the object was released, asc is oldest, desc is most recent
        * **id** - when it was added to moddb, asc is oldest, desc is most recent
        * **porder** - what plaform it's on???
        * **company** - company that made it in alphabetical order


    Attributes
    -----------
    name : str
        The name of the platform
    name_id : str
        The name_id of the member, cannot be changed, it's a mix of the original username lowercased with
        spaces removed and shortened.
    id : int
        The moddb id of the platform
    url : str
        The url of the platform page
    description : str
        Description of the platform
    company : Thumbnail
        A team like thumbnail of the company.
    homepage : str
        Link to the homepage of the engine
    date : datetime.datetime
        Date the engine was published
    stats : PlatformStatistics
        Stat data on the platform
    share : dict{str : str}
        Share link of the platform with the name of the share as key and link of the share as url.
    comments : CommentList[Comment]
        Comments on this page
    games : List[Thumbnail]
        A list of games suggested on the platform main page.
    hardware : List[Thumbnail]
        A list of hardware suggested on the platform main page.
    software : List[Thumbnail]
        A list of software suggested on the platform main page.
    engines : List[Thumbnail]
        A list of engines suggested on the platform main page.
    mods : List[Thumbnail]
        A list of mods suggested on the platform main page.
    """

    def __init__(self, html: BeautifulSoup):
        self.name = html.find("a", itemprop="mainEntityOfPage").string
        self.id = None

        self.url = join(html.find("a", itemprop="mainEntityOfPage")["href"])
        self.name_id = self.url.split("/")[0]
        try:
            self.description = html.find("div", id="profiledescription").p.string
        except AttributeError:
            self.description = html.find("p", itemprop="description").string

        try:
            company = html.find("h5", string="Company").parent.span.a
            self.company = Thumbnail(
                name=company.string, url=company["href"], type=ThumbnailType.team
            )
        except AttributeError:
            LOGGER.info(
                "Platform '%s' has no company", self.name, exc_info=LOGGER.level >= logging.DEBUG
            )
            self.company = None

        self.homepage = html.find("h5", string="Homepage").parent.span.a["href"]

        self.date = get_date(html.find("time", itemprop="releaseDate")["datetime"])

        self.stats = PlatformStatistics(html)

        try:
            share = html.find("h5", string="Share").parent.span.find_all("a")
            self.share = {
                "reddit": share[0]["href"],
                "mail": share[1]["href"],
                "twitter": share[2]["href"],
                "facebook": share[3]["href"],
            }
        except (AttributeError, IndexError):
            LOGGER.info(
                "Something funky about share box of platform '%s'",
                self.name,
                exc_info=LOGGER.level >= logging.DEBUG,
            )
            self.share = None

        self.comments = self._get_comments(html)

        hardware = (
            html.find("span", string=" Hardware")
            .parent.parent.parent.find("div", class_="table")
            .find_all("div", recursive=False)[:-1]
        )
        self.hardware = [
            Thumbnail(
                name=x.a["title"],
                url=x.a["href"],
                type=ThumbnailType.hardware,
                image=x.a.img["src"],
            )
            for x in hardware
        ]

        software = (
            html.find("span", string=" Software")
            .parent.parent.parent.find("div", class_="table")
            .find_all("div", recursive=False)[:-1]
        )
        self.software = [
            Thumbnail(
                name=x.a["title"],
                url=x.a["href"],
                type=ThumbnailType.software,
                image=x.a.img["src"],
            )
            for x in software
        ]

        engines = (
            html.find("span", string=" Engines")
            .parent.parent.parent.find("div", class_="table")
            .find_all("div", recursive=False)[:-1]
        )
        self.engines = [
            Thumbnail(
                name=x.a["title"],
                url=x.a["href"],
                type=ThumbnailType.engine,
                image=x.a.img["src"],
            )
            for x in engines
        ]

        mods = (
            html.find("span", string=" Mods")
            .parent.parent.parent.find("div", class_="table")
            .find_all("div", recursive=False)[:-1]
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

        games = (
            html.find("span", string=" Games")
            .parent.parent.parent.find("div", class_="table")
            .find_all("div", recursive=False)[:-1]
        )
        self.games = [
            Thumbnail(
                name=x.a["title"],
                url=x.a["href"],
                type=ThumbnailType.game,
                image=x.a.img["src"],
            )
            for x in games
        ]

    def __repr__(self):
        return f"<Platform name={self.name}>"
