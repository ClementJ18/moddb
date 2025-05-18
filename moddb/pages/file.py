import datetime
import re
import sys

import bs4
import requests

from ..boxes import Mirror, Thumbnail
from ..enums import AddonCategory, FileCategory, MediaCategory, ThumbnailType
from ..utils import (
    BASE_URL,
    concat_docs,
    get_date,
    get_page,
    get_views,
    join,
    prepare_request,
    raise_for_status,
)
from .base import BaseMetaClass

def parse_location(html) -> list[Thumbnail] | None:
    location = html.find("h5", string="Location").parent.find_all('a')
    if location is None:
        return None
    
    return [
        Thumbnail(
            type=ThumbnailType[location[x].string.lower()[:-1]], 
            url=location[x+1]["href"], 
            name=location[x+1].string,
        )
        for x in range(0, len(location)-1, 2)
    ]

@concat_docs
class File(BaseMetaClass):
    """An oject representing a file on ModDB, a file is something posted by the page owner which is directly linked
    to the page. It is endorsed by the page owner and they should do everythign they can to make sure that it is safe.
    As compared to an addon that may be added by fans to the page and that are files meant to work with the page but
    that are not directly related to the page. E.x the file of a mod page would be the mod files used to install the
    mod whereas an addon could be something like a fan-made texture pack for the mod or a map.

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
    category  : :class:`.FileCategory`
        The type of file (audio, video, demo, full version....)
    categoryaddon : :class:`.AddonCategory`
        The type of addon (map, textures, ect...)
    game : Union[:class:`.Game`, :class:`.Object`]
        An game object or an object with an id attribute which represents the
        game the file belongs to.
    timeframe : :class:`.TimeFrame`
        The time period this was released in (last 24hr, last week, last month)

    Sorting
    --------
        * **released** - when the object was released, asc is oldest, desc is most recent
        * **id** - when it was added to moddb, asc is oldest, desc is most recent
        * **ranktoday** - order by daily ranking, asc is highest ranked, desc is lowest rank
        * **visitstotal** - order by most views, asc is highest views, desc is lowest views
        * **rating** - order by rating, asc is highest rating, desc is lowest rating
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **date** - order by upload date, asc is most recent first, desc is oldest first

    Attributes
    -----------
    filename : str
        The name of the file
    hash : str
        The MD5 hash of the file
    name : str
        The name of the page
    size : int
        the file size in bytes
    today : int
        The number of downloads today
    downloads : int
        The total number of times this file has been downloaded
    category : FileCategory
        The category of the file
    author : Thumbnail
        A member type thumbnail of the member who uploaded the file
    date : datetime.datetime
        The date the file was uploaded
    button : str
        html code for the embed button
    widget : str
        html code for the embed widget
    description : str
        Description of the file, as written by the author
    preview : str
        URL of the preview image for the file
    location: list[Thumbnail]
        An ordered list detailing the hierarchy of entities the
        file or addon sits under. The last one being the entity
        directly attached to this file. 
    """

    def __init__(self, html: bs4.BeautifulSoup):
        if html.find("span", string="File Deleted", class_="heading"):
            raise ValueError("This file has been removed")

        info = html.find("div", class_="table tablemenu")
        file = {
            x.string.lower(): x.parent.span.string.strip()
            for x in info.find_all("h5", string=("Filename", "Size", "MD5 Hash"))
        }
        self.name = (
            html.find("a", title="Report").parent.parent.find("span", class_="heading").string
        )
        self.filename = file["filename"]
        super().__init__(html)

        self.hash = file["md5 hash"]
        self.size = int(re.sub(r"[(),bytes]", "", file["size"].split(" ")[1]))

        downloads = html.find("h5", string="Downloads").parent.a.string
        self.today = int(re.sub(r"[(),today]", "", downloads.split(" ")[1]))
        self.downloads = int(downloads.split(" ")[0].replace(",", ""))

        try:
            self.category = FileCategory(
                int(info.find("h5", string="Category").parent.a["href"].split("=")[-1])
            )
        except ValueError:
            self.category = AddonCategory(
                int(info.find("h5", string="Category").parent.a["href"].split("=")[-1])
            )

        uploader = info.find("h5", string="Uploader").parent.a
        self.author = Thumbnail(
            url=uploader["href"], name=uploader.string, type=ThumbnailType.member
        )

        self.date = get_date(info.find("h5", string="Added").parent.span.time["datetime"])
        self.button = info.find("h5", string="Embed Button").parent.span.input["value"]
        self.widget = info.find("h5", string="Embed Widget").parent.span.input["value"]

        self.description = html.find("p", id="downloadsummary").string

        self.preview = html.find_all("img", src=True)[0]["src"]

        self.location = parse_location(html)

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name} type={self.category.name}>"

    def save(self, file_obj, *, mirror=None):
        """Save the file to an object. This functions makes
        two requests. If you pass a valid mirror it will
        make only one request.

        Parameters
        -----------
        file_obj : typing.BinaryIO
            The file obj to save the file to. The binary data
            will be streamed to that object.
        mirror : Optional[Mirror]
            An optional mirror object to download the
            file from a specific moddb mirror

        """
        if mirror is None:
            download = get_page(f"{BASE_URL}/downloads/start/{self.id}")
            url = download.find("a", string=f"download {self.filename}")["href"]
        else:
            url = mirror._url

        SESSION = sys.modules["moddb"].SESSION
        prepped = prepare_request(requests.Request("GET", join(url)), SESSION)
        with SESSION.send(prepped, stream=True) as r:
            raise_for_status(r)
            for chunk in r.iter_content(chunk_size=8192):
                file_obj.write(chunk)

    def get_mirrors(self):
        """Get all the mirrors from which a file can be downloaded. This
        can then be passed to File.save to download from a specific mirror.


        Returns
        --------
        List[Mirror]
            A list of Mirror objects"""

        html = get_page(f"https://www.moddb.com/downloads/start/{self.id}/all")
        mirrors_div = html.find("div", class_="mirrors").find_all("div", recursive=False)
        mirrors = []
        for mirror in mirrors_div:
            mirror_match = re.match(
                r"(.*) #([0-9]*) \((\w+), (\w+)\)", mirror.div.p.contents[-1].strip()
            )
            stats_match = re.match(
                r"([0-9,]*) downloads? served, ([0-9.]*)% capacity",
                mirror.div.span.string,
            )

            mirrors.append(
                Mirror(
                    name=mirror_match.group(1),
                    index=int(mirror_match.group(2)),
                    city=mirror_match.group(3),
                    country=mirror_match.group(4),
                    served=int(stats_match.group(1).replace(",", "")),
                    capacity=float(stats_match.group(2)),
                    url=mirror.div.p.a["href"],
                )
            )

        return mirrors


@concat_docs
class Addon(File):
    """Object representing an addon. Seemingly the only difference between an addon and a file is in
    the semantics. A file often represents something official released by the page, e.g. the mod installation
    or an official guide where as addons are often fan made and might not be directly endorsed by the page owners
    even if it is allowed. They literally add on to the page's content without becoming part of it. There is a slight
    difference in their profiles but nothing beyond that.

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
    categoryaddon : :class:`.AddonCategory`
        The type of addon (map, textures, ect...)
    licence : :class:`.Licence`
        The licence of the addon
    game : Union[:class:`.Game`, :class:`.Object`]
        An game object or an object with an id attribute which represents the
        game the addon belongs to.
    timeframe : :class:`.TimeFrame`
        The time period this was released in (last 24hr, last week, last month)

    Sorting
    --------
        * **released** - when the object was released, asc is oldest, desc is most recent
        * **id** - when it was added to moddb, asc is oldest, desc is most recent
        * **ranktoday** - order by daily ranking, asc is highest ranked, desc is lowest rank
        * **visitstotal** - order by most views, asc is highest views, desc is lowest views
        * **rating** - order by rating, asc is highest rating, desc is lowest rating
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **licence** - order based on licence
        * **date** - order by upload date, asc is most recent first, desc is oldest first


    """

    pass


@concat_docs
class Media(BaseMetaClass):
    """Represents an image, audio file or video file on

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    -----------
    sitearea : :class:`.Category`
        The type of model the media belongs to. Category.downloads is not valid for this.

    Sorting
    --------
        * **ranktoday** - order by daily ranking, asc is highest ranked, desc is lowest rank
        * **visitstotal** - order by most views, asc is highest views, desc is lowest views
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **id** - order by upload date, asc is most recent first, desc is oldest first

        Exclusive to videos and audios
        * **duration** - order by duration, asc is shortest to longest, desc is longest first

    Attributes
    -----------
    date : datetime.datetime
        The date the media was uploaded
    name : str
        The name of the media
    author : Thumbnail
        Member type thumbnail of the media uploader
    duration : datetime.timedelta
        Duration of the media in seconds, 0 if it's an image
    size : int
        Size of the files in bytes
    views : int
        Total amount of views
    today : int
        Amount of views today
    filename : str
        The name of the file for the media
    fileurl : str
        The url of the file for the media
    category : MediaCategory
        Whether the media is an image, a video or an audio
    description : str
        The description of the file as given by the file uploader.
    """

    def __init__(self, html: bs4.BeautifulSoup):
        try:
            self.name = html.find("meta", itemprop="name")["content"]
        except TypeError:
            self.name = html.find("img", id="mediaimage")["title"]

        super().__init__(html)
        medias = html.find_all("h5", string=("Date", "By", "Duration", "Size", "Views", "Filename"))
        raw_media = {media.string.lower(): media.parent for media in medias}

        self.date = get_date(raw_media["date"].span.time["datetime"])

        author = raw_media["by"].span.a
        self.author = Thumbnail(
            url=author["href"], name=author.string.strip(), type=ThumbnailType.member
        )

        if "duration" in raw_media:
            duration = raw_media["duration"].span.time.string.strip().split(":")
            duration.reverse()
            times = ["seconds", "minutes", "hours"]
            self.duration = datetime.timedelta(
                **{times[duration.index(x)]: int(x) for x in duration}
            )
        else:
            self.duration = 0

        if "size" in raw_media:
            self.size = tuple(raw_media["size"].span.string.strip().split("×"))

        self.views, self.today = get_views(raw_media["views"].a.string)
        media_player = html.find("video", id="mediaplayer")

        if not media_player:
            self.category = MediaCategory.image
            self.fileurl = html.find("meta", property="og:image")["content"]
        else:
            self.fileurl = media_player.source["src"]
            if "audio" in media_player.source["type"]:
                self.category = MediaCategory.audio
            else:
                self.category = MediaCategory.video

        if "filename" in raw_media:
            self.filename = raw_media["filename"].span.string.strip()
        else:
            self.filename = self.fileurl.split("/")[-1]

        self.description = html.find("meta", {"name": "description"})["content"]

    def __repr__(self):
        return f"<Media name={self.name} type={self.category.name}>"

    def save(self, file_obj):
        """Save the media to an object.

        Parameters
        -----------
        file_obj : typing.BinaryIO
            The file obj to save the file to. The binary data
            will be streamed to that object.

        """
        SESSION = sys.modules["moddb"].SESSION
        prepped = prepare_request(requests.Request("GET", self.fileurl), SESSION)

        with SESSION.send(prepped, stream=True) as r:
            raise_for_status(r)
            for chunk in r.iter_content(chunk_size=8192):
                file_obj.write(chunk)
