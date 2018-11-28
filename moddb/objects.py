from .enums import *

import re
import datetime
import requests
from bs4 import BeautifulSoup
import sys

class Parser:
    def get_author(self):
        r = requests.get(self._author)
        soup = BeautifulSoup(r.text, "html.parser")
        return User.parse(soup)

    def get_comments(self, index : int):
        r = requests.get(self.url + f"/page/{index}#comments")
        soup = BeautifulSoup(r.text, "html.parser")

        comments = []
        for div in soup.find("div", class_="table tablecomments").find_all("div"):
            if div.find("div", class_="content") is not None:
                comments.append(Comment.parse(div))

        return comments

class RequestMaker:
    pass

class Page(Parser):
    def __init__(self, **attrs):
        self._html = attrs.pop("html")
        self.stats = Statistics.parse(self._html)
        self.style = Style.parse(self._html)
        self.url = attrs.pop("url")
        self.files = []
        self.comments = []

        for file in self._html.parent.parent.parent.find("div", class_="inner").find_all("div")[2].find_all("div"):
            if file.a.string is not None:
                self.files.append(Thumbnail.parse(file, "file"))

        for div in self._html.find("div", class_="table tablecomments").find_all("div"):
            if div.find("div", class_="content") is not None:
                self.comments.append(Comment.parse(div))

    def get_files(self, index : int):
        r = requests.get(self.url + f"/downloads/page/{index}")
        soup = BeautifulSoup(r.text, "html.parser")

        files = []
        for file in soup.parent.parent.parent.find("div", class_="table").find_all("div")[2].find_all("div"):
            if file.a.string is not None:
                files.append(Thumbnail.parse(file, "file"))

        return files

class Game:
    pass

class Mod:
    pass

class File(Parser):
    def __init__(self, **attrs):
        self.name = attrs.pop("filename")
        self.category = attrs.pop("category")
        self.uploader = attrs.pop("uploader")
        self._author = attrs.pop("author")
        self.date = attrs.pop("date")
        self.size = attrs.pop("size")
        self.downloads = attrs.pop("downloads")
        self.today = attrs.pop("today")
        self.button = attrs.pop("button")
        self.widget = attrs.pop("widget")
        self.description = attrs.pop("description")
        self.hash = attrs.pop("md5 hash")
        self.preview = attrs.pop("preview")

    def __repr__(self):
        return f"<File name={self.name}>"

    @classmethod
    def parse(cls, html):
        files_headings = ("Filename", "Size", "MD5 Hash")
        info = html.find("div", class_="table tablemenu")
        t = [t for t in info.find_all("h5") if t.string in files_headings]

        file = {x.string.lower() : x.parent.span.string.strip() for x in info.find_all("h5") if x.string in files_headings}
        file["downloads"] = info.find("h5", string="Downloads").parent.a.string


        file["size"] = int(re.sub(r"[(),bytes]", "", file["size"].split(" ")[1]))
        file["today"] = int(re.sub(r"[(),today]", "", file["downloads"].split(" ")[1]))
        file["downloads"] = int(file["downloads"].split(" ")[0].replace(",", ""))

        file["category"] = FileCategory(int(info.find("h5", string="Category").parent.a["href"][-1]))
        uploader = info.find("h5", string="Uploader").parent.a
        file["uploader"] = uploader.string
        file["author"] = uploader["href"]

        d = info.find("h5", string="Added").parent.span.time["datetime"]
        d = d[:-3] + d[-2:]
        file["date"] = datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S%z')

        file["button"] = info.find("h5", string="Embed Button").parent.span.input["value"]
        file["widget"] = info.find("h5", string="Embed Widget").parent.span.input["value"]


        file["description"] = html.find("p", id="downloadsummary").string
        file["preview"] = html.find_all("img")[0]["src"]

        return cls(**file)


class Media(Parser):
    def __init__(self, **attrs):
        self.name = attrs.pop("name")
        self.type = attrs.pop("type")
        self.url = attrs.pop("url")
        self.duration = attrs.pop("duration", None)
        self.size = attrs.pop("size", None)
        self.views = attrs.pop("views")
        self.today = attrs.pop("today")
        self.filename = attrs.pop("filename", None)
        self.submitter = attrs.pop("submitter")
        self._author = attrs.pop("author")
        self.description = attrs.pop("description")
        self.date = attrs.pop("date")


    @classmethod
    def parse(cls, html):
        media = {}
        media_headings = ("Date", "By", "Duration", "Size", "Views", "Filename")
        raw_media = {media.string.lower() : media.parent for media in html.find_all("h5") if media.string in media_headings}

        d = raw_media["date"].span.time["datetime"]
        d = d[:-3] + d[-2:]
        media["date"] = datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S%z')

        media["author"] = raw_media["by"].span.a["href"]
        media["submitter"] = raw_media["by"].span.a.string.strip()

        if "duration" in raw_media:
            duration = raw_media["duration"].span.time.string.strip().split(":")
            media["duration"] = (int(duration[0]) * 60) + int(duration[1])

        if "size" in raw_media:
            media["size"] = tuple(raw_media["size"].span.string.strip().split("×"))

        media["today"] = int(re.sub(r"[(),today]", "", raw_media["views"].span.a.string.split(" ")[1]))
        media["views"] = int(raw_media["views"].span.a.string.split(" ")[0].replace(",", ""))

        if "filename" in raw_media:
            media["filename"] = raw_media["filename"].span.string.strip()

        if "size" in media and "duration" in media:
            media["type"] = MediaCategory.video
            media["url"] = html.find("meta", property="og:image")["content"][:-4]
        elif "size" in media:
            media["type"] = MediaCategory.image
            media["url"] = html.find("meta", property="og:image")["content"]
        else:
            media["type"] = MediaCategory.audio
            media["url"] = html.find("video", id="mediaplayer").find("source")["src"]


        media["description"] = html.find("meta", {"name":"description"})["content"]
        media["name"] = html.find("meta", property="og:title")["content"]

        return cls(**media)



#article, blog, headlines
class Article(Parser):
    def __init__(self, **attrs):
        self._author = attrs.pop("author")
        self.title = attrs.pop("title")
        self.date = attrs.pop("date")
        self.suggestions = attrs.pop("suggestions")
        self.content = attrs.pop("content")
        self.plaintext = self._plaintext(self.content)
        self.type = attrs.pop("type")

    def _plaintext(self, html):
        pass

    @classmethod
    def parse(cls, html):
        pass

class Engine(Parser):
    pass

class Team(Parser):
    pass

class Group(Parser):
    pass

class Job(Parser):
    pass

class Addon(Parser):
    pass

class Thumbnail:
    def __init__(self, **attrs):
        self.url = attrs.pop("url")
        self.name = attrs.pop("name")
        self.image = attrs.pop("image")
        self.type = attrs.pop("type")

    def __repr__(self):
        return f"<Thumbnail name={self.name} type={self.type}>"

    @classmethod
    def parse(cls, html, type):
        thumbnail = {}

        thumbnail["url"] = html.a["href"]
        thumbnail["name"] = html.a.string
        thumbnail["type"] = ThumbnailType[type]
        thumbnail["image"] = html.find("img", alt=thumbnail["name"])

        return cls(**thumbnail)

    def parse_thumbnail(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        return getattr(sys.modules[__name__], self.type.name.title()).parse(soup)

class Comment(Parser):
    def __init__(self, **attrs):
        self.name = attrs.pop("name")
        self._author = attrs.pop("author")
        self.date = attrs.pop("date")
        self.content = attrs.pop("content")
        self.karma = attrs.pop("karma")
        self.upvote = attrs.pop("upvote")
        self.downvote = attrs.pop("downvote")
        self.position = attrs.pop("position")

    def __repr__(self):
        return f"<Comment author={self.name} position={self.position}>"

    @classmethod
    def parse(cls, html):
        comment = {}
        div = html.find("div", class_="content")
        heading = div.find("span", class_="heading")
        comment["author"] = heading.a["href"]
        comment["name"] = heading.a.string
        d = heading.time["datetime"]
        d = d[:-3] + d[-2:]
        comment["date"] = datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S%z')
        comment["content"] = div.find("div", class_="comment").p.string
        actions = div.find("span", class_="actions").find_all("a")
        karma = div.find("span", class_="actions").span.string
        comment["karma"] = int(re.findall(r"[+-]?\d", karma)[0])
        comment["upvote"] = actions[1]["href"]
        comment["downvote"] = actions[2]["href"]
        position = html["class"] 

        if "reply1" in position:
            comment["position"] = 1
        elif "reply2" in position:
            comment["position"] = 2
        else:
            comment["position"] = 0

        return cls(**comment)

    def get_comment(self):
        raise NotImplementedError


class User(Parser):
    pass

    def get_author(self):
        raise NotImplementedError


class Statistics:
    def __init__(self, **attrs):
        self.rank = int(attrs.pop("rank"))
        self.total = int(attrs.pop("total"))
        self.visits = int(attrs.pop("visits"))
        self.today = int(attrs.pop("today"))
        self.updated = attrs.pop("updated")
        self.followers = int(attrs.pop("watchers"))
        self.files = int(attrs.pop("files"))
        self.articles = int(attrs.pop("articles"))
        self.reviews = int(attrs.pop("reviews"))
        self.mods = int(attrs.pop("mods")) if "mods" in attrs else None

    @classmethod
    def parse(cls, html):
        titles = ("Rank", "Visits", "Files", "Articles", "Reviews", "Watchers", "Mods")

        misc = html.find_all("h5")
        stats = {stat.string.lower() : stat.parent.a.string.replace(",", "").replace(" members", "") for stat in misc if stat.string in titles}
        
        match = re.findall(r"\((\d*) .*\)", stats["visits"])
        stats["today"] = match[0]
        stats["visits"] = re.sub(r"\(.*\)", "", stats["visits"])

        rank = stats["rank"].split("of")
        stats["rank"] = rank[0]
        stats["total"] = rank[1]

        for item in misc:
            if item.string == "Last Update":
                d = item.parent.span.time["datetime"]
                d = d[:-3] + d[-2:]
                stats["updated"] = datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S%z')

        return cls(**stats)

#mod, game, user, addon, engine, company, group
class Profile:
    def __init__(self, **attrs):
        for key, value in attrs.items():
            setattr(self, key, value)

    @classmethod
    def parse(cls, html):
        page_type = SearchCategory[html.find("div", id="subheader").find("ul", class_="tabs").find("li", class_="on").a.string]
        
        profile_raw = html.find("span", string="Profile").parent.parent.parent.find("div", class_="table tablemenu")
        profile = {}

        profile["contact"] = profile_raw.find("h5", string="Contact").parent.span.a["href"]
        profile["follow"] = [x for x in profile_raw.find_all("h5") if x.string in ["Mod watch", "Game watch", "Group watch", "Engine watch"]][0]
        share = profile_raw.find("h5", string="Share").parent.span.find_all("a")
        profile["share"] = {
            "reddit": share[0]["href"],
            "mail": share[1]["href"],
            "twitter": share[2]["href"],
            "facebook": share[3]["href"]
        }

        if page_type in [SearchCategory.developers, SearchCategory.groups]:
            profile["private"] = profile_raw.find("h5", string="Privacy").parent.span.string.strip() != "Public"

            membership = profile_raw.find("h5", string="Subscription").parent.span.string.strip()
            if membership == "Open to all members":
                profile["membership"] = Membership(3)
            elif membership == "Must apply to join":
                profile["membership"] = Membership(2)
            else:
                profile["membership"] = Membership(1)

        if page_type in [SearchCategory.games, SearchCategory.mods]:
            profile["icon"] = profile_raw.find("h5", string="Icon").parent.span.img["src"]

        if page_type in [SearchCategory.games, SearchCategory.mods, SearchCategory.engines]:
            profile["team"] = [x.parent.a.string for x in profile_raw.find_all("h5") if x.string in ["Developer", "Publisher", "Developer & Publisher","Creator", "Company"]][0]
            d = profile_raw.find("h5", string="Release date").parent.span.time["datetime"]
            profile["release"] = datetime.datetime.strptime(d, "%Y-%m-%d")

        if page_type != SearchCategory.groups:
            profile["homepage"] =  profile_raw.find("h5", string="Homepage").parent.span.a["href"]

        if page_type == SearchCategory.games:
            profile["engine"] = profile_raw.find("h5", string="Engine").parent.span.a["href"]
            profile["engine_name"] = profile_raw.find("h5", string="Engine").parent.span.a.string

        if page_type == SearchCategory.mods:
            profile["game"] = profile_raw.find("h5", string="Game").parent.span.a["href"]
            profile["game_name"] = profile_raw.find("h5", string="Game").parent.span.a.string

        if page_type == SearchCategory.engines:
            profile["license"] = License(int(profile_raw.find("h5", string="Licence").parent.span.a["href"][-1]))

        if page_type in [SearchCategory.games, SearchCategory.engines]:
            profile["platform"] = [x.string for x in profile_raw.find("h5", string="Platforms").parent.span.span.find_all("a")]


        return cls(**profile)

class Style:
    def __init__(self, **attrs):
        self.genre = attrs.pop("genre")
        self.theme = attrs.pop("theme")
        self.players = attrs.pop("players")

    @classmethod
    def parse(cls, html):
        titles = ("Theme", "Genre", "Players")

        misc = html.find_all("h5")
        styles = {style.string.lower() : re.findall(r"(\d*)$", style.parent.a["href"])[0] for style in misc if style.string in titles}

        styles["theme"] = Theme(int(styles["theme"]))
        styles["genre"] = Genre(int(styles["genre"]))
        styles["players"] = PlayerStyle(int(styles["players"])) 

        return cls(**styles)

class Filter:
    def __init__(self, **kwarg):
        self.released = kwarg.get("released", None)
        self.genre = kwarg.get("genre", None)

    def set_genre(self, genre):
        if isinstance(genre, Genre):
            self.genre = genre.name
        elif genre is None:
            self.genre = genre
        else:
            raise ValueError("Must be Genre enum or None")

    def set_theme(self, theme):
        if isinstance(theme, Theme):
            self.theme = theme.name
        elif genre is None:
            self.theme = genre
        else:
            raise ValueError("Must be Theme enum or None")
