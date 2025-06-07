import re

import bs4

from ..boxes import Thumbnail
from ..enums import ThumbnailType
from ..utils import LOGGER, get_page, get_page_type, join
from . import opinion


class FrontPage:
    """An object representing the front page of  More of less just a long suggestion of the hottest mods,
    games, articles and files of the moment

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Attributes
    -----------
    slider : List[Thumnail]
        A list of object like thumbnails presented by the slider present on
        the front page, this is a catered list of promoted content, can contain
        any type of object.
    articles : List[Thumbnail]
        A list of article like thumbnail objects representing the suggested
        articles on the front page.
    mods : List[Thumbnail]
        A list of mod like thumbnail objects representing the suggested
        mods on the front page.
    games : List[Thumbnail]
        A list of game like thumbnail objects representing the suggested
        games on the front page.
    files : List[Thumbnail]
        A list of file like thumbnail objects representing the suggested
        files on the front page.
    poll_url : str
        The url to the poll on the front page
    """

    def __init__(self, html: bs4.BeautifulSoup):
        slider = html.find("div", class_="rotatorholder").find_all("div", class_="rotatorbox")
        self.slider = []
        for x in slider:
            name = x.a.find("h2")
            summary = x.a.find("p")

            image = None
            if "style" in x.div:
                re_search = re.search(r"\((.*)\)", x.div["style"])
                if re_search:
                    image = re_search.group(1)
            elif "data-bg" in x.div:
                image = x.div["data-bg"]

            try:
                page_type = get_page_type(x.a["href"])
            except IndexError:
                LOGGER.warning(
                    "Unabled to get page type from %s for front page, skipping", x.a["href"]
                )
                continue

            thumbnail = Thumbnail(
                name=name.string if name else None,
                url=x.a["href"],
                summary=summary.string if summary else None,
                image=image,
                type=page_type,
            )

            self.slider.append(thumbnail)

        articles = (
            html.find("span", string="Latest Articles")
            .parent.parent.parent.find("div", class_="table")
            .find_all("div", recursive=False)[:-1]
        )
        self.articles = [
            Thumbnail(
                name=x.a["title"],
                url=x.a["href"],
                type=ThumbnailType.article,
                image=x.a.img["src"],
                summary=x.find("p").string,
                date=x.find("time")["datetime"],
            )
            for x in articles
        ]

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

        games = (
            html.find("span", string="Popular Games")
            .parent.parent.parent.find("div", class_="table")
            .find_all("div", recursive=False)[1:]
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

        jobs = (
            html.find("span", string="Jobs")
            .parent.parent.parent.find("div", class_="table")
            .find_all("div", recursive=False)[1:]
        )
        self.jobs = [
            Thumbnail(
                name=x.find("a").string,
                url=x.find("a")["href"],
                type=ThumbnailType.job,
            )
            for x in jobs
        ]

        files = (
            html.find("span", string="Popular Files")
            .parent.parent.parent.find("div", class_="table")
            .find_all("div", recursive=False)[1:]
        )
        self.files = [
            Thumbnail(
                name=x.a["title"],
                url=x.a["href"],
                type=ThumbnailType.file,
                image=x.a.img["src"],
            )
            for x in files
        ]

        try:
            # maybe they haven't voted yet and the vote bar is there
            self.poll_url = html.find("div", class_="poll").form["action"]
        except AttributeError:
            # maybe they've already voted and the result link is there
            self.poll_url = join(
                html.find("div", class_="poll").find("a", class_="results")["href"]
            )

        self._html = html
        self._poll = None

    def __repr__(self):
        return f"<FrontPage articles={len(self.articles)} mods={len(self.mods)} games={len(self.games)} files={len(self.files)}>"

    def get_poll(self) -> opinion.Poll:
        """Get the full item of the front page poll. This
        result is cached after the first call.

        Returns
        --------
        Poll
            The returned poll
        """
        if self._poll is None:
            self._poll = opinion.Poll(get_page(self.poll_url))

        return self._poll
