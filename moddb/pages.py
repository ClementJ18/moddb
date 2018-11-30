from .boxes import *

import re
import datetime
import requests
from bs4 import BeautifulSoup

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
        self._html = attrs.get("html")
        self.stats = Statistics.parse(self._html)
        self.style = Style.parse(self._html)
        self.url = attrs.get("url")
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
        self.name = attrs.get("filename")
        self.category = attrs.get("category")
        self.uploader = attrs.get("uploader")
        self._author = attrs.get("author")
        self.date = attrs.get("date")
        self.size = attrs.get("size")
        self.downloads = attrs.get("downloads")
        self.today = attrs.get("today")
        self.button = attrs.get("button")
        self.widget = attrs.get("widget")
        self.description = attrs.get("description")
        self.hash = attrs.get("md5 hash")
        self.preview = attrs.get("preview")

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
        self.name = attrs.get("name")
        self.type = attrs.get("type")
        self.url = attrs.get("url")
        self.duration = attrs.get("duration", None)
        self.size = attrs.get("size", None)
        self.views = attrs.get("views")
        self.today = attrs.get("today")
        self.filename = attrs.get("filename", None)
        self.submitter = attrs.get("submitter")
        self._author = attrs.get("author")
        self.description = attrs.get("description")
        self.date = attrs.get("date")


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

        matches = re.search(r"^([0-9,]*) \(([0-9,]*) today\)$", raw_media["views"])
        media["views"] = int(matches.group(1).replace(",", ""))
        media["today"] = int(matches.group(2).replace(",", ""))

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
        self.author = attrs.get("author")
        self.title = attrs.get("title")
        self.date = attrs.get("date")
        self.html = attrs.get("html")
        self.type = attrs.get("type")
        self.profile = attrs.get("profile")
        self.tags = attrs.get("tags")
        self.report = attrs.get("report")
        self.views = attrs.get("views")
        self.today = attrs.get("today")
        self.share = attrs.get("share")
        self.introduction = attrs.get("introdution")
        self.plaintext = attrs.get("plaintext")

    @classmethod
    def parse(cls, html):
        article = {}
        raw_type = html.find("h5", string="Browse").parent.span.a.string
        article["type"] = ArticleType[raw_type.lower()]

        try:
            raw = html.find("span", string=raw_type[0:-1]).parent.parent.parent.find("div", class_="table tablemenu")
        except AttributeError:
            raw = html.find("span", string=raw_type).parent.parent.parent.find("div", class_="table tablemenu")

        article["profile"] = Profile.parse(html)

        article["tags"] = {x.string : x["href"] for x in raw.find("h5", string="Tags").parent.span.find_all("a") if x is not None}
        article["report"] = raw.find("h5", string="Report").parent.span.a["href"]
        
        views_raw = raw.find("h5", string="Views").parent.span.a.string
        matches = re.search(r"^([0-9,]*) \(([0-9,]*) today\)$", views_raw)
        article["views"] = int(matches.group(1).replace(",", ""))
        article["today"] = int(matches.group(2).replace(",", ""))

        share = raw.find("h5", string="Share").parent.span.find_all("a")
        article["share"] = {
            "reddit": share[0]["href"],
            "mail": share[1]["href"],
            "twitter": share[2]["href"],
            "facebook": share[3]["href"]
        }

        article["title"] = html.find("span", itemprop="headline").string
        article["introdution"] = html.find("p", itemprop="description").string
        author = html.find("span", itemprop="author").span.a
        article["author"] = Thumbnail(name=author.string, url=author["href"], type=ThumbnailType.user)


        d = html.find("time", itemprop="datePublished")["datetime"]
        d = d[:-3] + d[-2:]
        article["date"] = datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S%z')

        article["html"] = str(html.find("div", itemprop="articleBody"))
        article["plaintext"] = html.find("div", itemprop="articleBody").text

        return cls(**article)




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
    def get_author(self):
        raise NotImplementedError
