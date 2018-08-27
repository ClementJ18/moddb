from .enums import *

import re
import datetime
import requests
from bs4 import BeautifulSoup

BASE_PATH = "https://www.moddb.com"

class Parser:
    def _page_parse(self, url, *, type=None):
        pass

class RequestMaker:
    pass

class Page:
    def __init__(self, **attrs):
        self._html = attrs.pop("html")
        self.stats = Statistics.parse(self._html)
        self.style = Style.parse(self._html)
        self.url = attrs.pop("url")

    def get_comments(self, index : int):
        r = requests.get(BASE_PATH + self.url + f"/page/{index}#comments")
        soup = BeautifulSoup(r.text, "html.parser")

        comments = {}
        for div in soup.find("div", class_="table tablecomments").find_all("div"):
            if not div.find("div", class_="content") is None:
                comments.append(Comment.parse(div))

        return comments

class Game:
    pass

class Mod:
    pass

class File:
    pass

class Media:
    pass

#article, blog, headlines
class Article:
    def __init__(self, **attrs):
        self._author = attrs.pop("author")
        self.title = attrs.pop("title")
        self.date = attrs.pop("date")
        self.suggestions = attrs.pop("suggestions")
        self.content = attrs.pop("content")
        self.plaintext = self._plaintext(self.content)
        self.type = attrs.pop("type")

    def get_author(self):
        r = requests.get(BASE_PATH + self._author)
        soup = BeautifulSoup(r.text, "html.parser")
        return User.parse(soup)

    def _plaintext(self, html):
        pass

    @classmethod
    def parse(cls, html):
        pass

class Engine:
    pass

class Team:
    pass

class Group:
    pass

class Job:
    pass

class Addon:
    pass

class Thumbnail:
    def __init__(self, **attrs):
        pass

    @classmethod
    def parse(cls, html):
        pass

    def parse_thumbnail(self):
        pass

class Comment:
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
        comment["author"] = BASE_PATH + heading.a["href"]
        comment["name"] = heading.a.string
        d = heading.time["datetime"]
        d = d[:-3] + d[-2:]
        comment["date"] = datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S%z')
        comment["content"] = div.find("div", class_="comment").p.string
        actions = div.find("span", class_="actions").find_all("a")
        karma = div.find("span", class_="actions").span.string
        comment["karma"] = int(re.findall(r"[+-]?\d", karma)[0])
        comment["upvote"] = BASE_PATH + actions[1]["href"]
        comment["downvote"] = BASE_PATH + actions[2]["href"]
        position = html["class"] 

        if "reply1" in position:
            comment["position"] = 1
        elif "reply2" in position:
            comment["position"] = 2
        else:
            comment["position"] = 0

        return cls(**comment)


class User:
    pass

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
        pass

    @classmethod
    def parse(cls, html):
        pass

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
