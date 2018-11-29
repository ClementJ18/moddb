from .boxes import *

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
        news_raw = html.find("span", string="News").parent.parent.parent.find("div", class_="table tablemenu")
        profile = Profile.parse(html)

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

class User(Parser):
    pass

    def get_author(self):
        raise NotImplementedError


