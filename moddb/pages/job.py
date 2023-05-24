import bs4
import json
import re

from ..utils import join, LOGGER
from ..boxes import PartialTag, Thumbnail
from ..enums import ThumbnailType, JobSkill


class Job:
    """Model representing a job proposed on ModDB

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
    skill : :class:`.JobSkill`
        The job skill looked for
    earn : :class:`.bool`
        Whether or not the job is paid

    Sorting
    --------
        * **location** - order by the location of the job
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **skill** - order by the skill required
        * **id** - order by upload date, asc is most recent, desc is oldest first

    Attributes
    -----------
    id : int
        id of the job
    name_id : str
        The name_id of the member, cannot be changed, it's a mix of the original username lowercased with
        spaces removed and shortened.
    author : Thumbnail
        A member like thumbnail representing the poster of the job. Can be none if they desire to remain private.
    paid : bool
        Whether or not the job is paid
    tags : List[PartialTag]
        A list of partial tags. You can use `get_tags` and then use the name id to get the right one.
    skill : JobSkill
        the skill demanded for the job
    location : str
        The location the job will be at
    name : str
        The name of the job
    text : str
        The description of the job
    related : List[Thumbnail]
        A list of team like thumbnails of companies related to the job poster

    """

    def __init__(self, html: bs4.BeautifulSoup):
        breadcrumb = json.loads(html.find("script", type="application/ld+json").string)[
            "itemListElement"
        ][-1]["Item"]
        self.name = breadcrumb["name"]
        self.url = breadcrumb["@id"]
        self.name_id = self.url.split("/")[0]
        self.text = html.find("div", id="articlecontent").text

        profile_raw = html.find("span", string="Jobs").parent.parent.parent.find(
            "div", class_="table tablemenu"
        )

        self.id = int(re.search(r"siteareaid=(\d*)", html.find("a", string="Report")["href"])[1])

        try:
            author = profile_raw.find("h5", string="Author").parent.span.a
            self.author = Thumbnail(
                url=author["href"], name=author.string, type=ThumbnailType.member
            )
        except AttributeError:
            LOGGER.info("Job '%s' has no author", self.name)
            self.author = None

        self.paid = profile_raw.find("h5", string="Paid").parent.a.string == "Yes"

        try:
            raw_tags = html.find("form", attrs={"name": "tagsform"}).find_all("a")
            self.tags = [
                PartialTag(x.string, join(x["href"]), x["href"].split("/")[-1])
                for x in raw_tags
                if x.string is not None
            ]
        except AttributeError:
            self.tags = []
            LOGGER.info("'%s' '%s' has no tags", self.__class__.__name__, self.name)

        self.skill = JobSkill(int(profile_raw.find("h5", string="Skill").parent.span.a["href"][-1]))

        self.location = profile_raw.find("h5", string="Location").parent.span.string.strip()

        try:
            related = html.find("div", class_="tablerelated").find_all("a", class_="image")
            self.related = [
                Thumbnail(url=x["href"], name=x["title"], type=ThumbnailType.team) for x in related
            ]
        except AttributeError:
            LOGGER.info("Job '%s' has no related companies", self.name)
            self.related = []

        self._html = html

    def __repr__(self):
        return f"<Job name={self.name}>"
