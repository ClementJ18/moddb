import requests
import datetime
import re

from .enums import *

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
        self.contact = attrs.get("contact")
        self.follow = attrs.get("follow")
        self.share = attrs.get("share")

        #developers, groups
        self.private = attrs.get("private", None)
        self.membership = attrs.get("membership", None)

        #games, mods
        self.icon = attrs.get("icon", None)

        #games, mods, engines
        self.developers = attrs.get("developers", None)
        self.release = attrs.get("release", None)

        #games, mods, engines, developers
        self.homepage = attrs.get("homepage", None)

        #mods
        self.game = attrs.get("game", None)

        #games
        self.engine = attrs.get("engine", None)

        #engines
        self.license = attrs.get("license", None)

        #games, engines
        self.platform = attrs.get("platform", None)

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

        if page_type in [SearchCategory.games, SearchCategory.mods, SearchCategory.addon]:
            profile["icon"] = profile_raw.find("h5", string="Icon").parent.span.img["src"]

        if page_type in [SearchCategory.games, SearchCategory.mods, SearchCategory.engines, SearchCategory.addon]:
            #ToDo: in the future support having different develope/publisher/creator/company
            profile["developers"] = [x.parent.a.string for x in profile_raw.find_all("h5") if x.string in ["Developer", "Publisher", "Developer & Publisher","Creator", "Company"]][0]
            d = profile_raw.find("h5", string="Release date").parent.span.time["datetime"]
            profile["release"] = datetime.datetime.strptime(d, "%Y-%m-%d")

        if page_type != SearchCategory.groups:
            profile["homepage"] =  profile_raw.find("h5", string="Homepage").parent.span.a["href"]

        if page_type in [SearchCategory.games, SearchCategory.addon]:
            url = profile_raw.find("h5", string="Engine").parent.span.a["href"]
            name = profile_raw.find("h5", string="Engine").parent.span.a.string
            profile["engine"] = Thumbnail(url=url, name=name, type=ThumbnailType.engine)

        if page_type == SearchCategory.mods:
            url = profile_raw.find("h5", string="Game").parent.span.a["href"]
            name = profile_raw.find("h5", string="Game").parent.span.a.string
            profile["game"] = Thumbnail(url=url, name=name, type=ThumbnailType.game)

        if page_type == SearchCategory.engines:
            profile["license"] = License(int(profile_raw.find("h5", string="Licence").parent.span.a["href"][-1]))

        if page_type in [SearchCategory.games, SearchCategory.engines, SearchCategory.addon]:
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

class Thumbnail:
    def __init__(self, **attrs):
        self.url = attrs.pop("url")
        self.name = attrs.pop("name")
        self.image = attrs.pop("image", None)
        self.type = attrs.pop("type")

    def __repr__(self):
        return f"<Thumbnail name={self.name} type={self.type}>"

    @classmethod
    def parse(cls, html, type):
        thumbnail = {
            "url": html.a["href"],
            "name": html.a.string,
            "type": ThumbnailType[type],
            "image":html.find("img", alt=thumbnail["name"])
        }

        return cls(**thumbnail)

    def parse_thumbnail(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        return getattr(sys.modules[__name__], self.type.name.title()).parse(soup)

class Comment():
    def __init__(self, **attrs):
        self.name = attrs.pop("name")
        self.author = attrs.pop("author")
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
        
        #author
        url = heading.a["href"]
        name = heading.a.string
        comment["author"] = Thumbnail(url=url, name=name, type=ThumbnailType.user)
        
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
