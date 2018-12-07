from .enums import ThumbnailType, SearchCategory, Membership, License, Genre, Theme, PlayerStyle
from .utils import get_date, soup, get_views, join, normalize, LOGGER

import sys
import re

__all__ = ['CommentsList', 'Statistics', 'Profile', 'Style', 'Thumbnail', 
           'Comment', 'Review', 'UserProfile', 'UserStatistics']

class CommentsList(list):
    def flatten(self):
        top_list = []
        for comment in super().__iter__():
            top_list.append(comment)
            for child in comment.children:
                top_list.append(child)
                top_list.extend(child.children)

        return top_list
    

class Statistics:
    def __init__(self, html):
        misc = html.find_all("h5", string=("Files", "Articles", "Reviews", "Watchers", "Mods"))
        self.__dict__.update({stat.string.lower() : int(normalize(stat.parent.a.string)) for stat in misc})

        visits = normalize(html.find("h5", string="Visits").parent.a.string)
        self.visits, self.today = get_views(visits)

        rank = normalize(html.find("h5", string="Rank").parent.a.string).split("of")
        self.rank = int(rank[0].replace(",", ""))
        self.total = int(rank[1].replace(",", ""))

        self.updated = get_date(html.find("time", itemprop="dateModified")["datetime"])

    def __repr__(self):
        return f"<Statistics rank={self.rank}/{self.total}>"

#mod, game, user, addon, engine, company, group
class Profile:
    def __init__(self, html):
        self.__dict__.update({
            "private": None,
            "membership": None,
            "icon": None,
            "developers": None,
            "release": None,
            "homepage": None,
            "game": None,
            "engine": None,
            "license": None,
            "platform": []
            })

        try:
            _name = html.find("a", itemprop="mainEntityOfPage").string
        except AttributeError:
            _name = html.find("span", itemprop="headline").string
            
        page_type = SearchCategory[html.find("div", id="subheader").find("ul", class_="tabs").find("li", class_="on").a.string]
        
        profile_raw = html.find("span", string="Profile").parent.parent.parent.find("div", class_="table tablemenu")
        self.type = page_type
        self.contact = join(profile_raw.find("h5", string="Contact").parent.span.a["href"])
        self.follow = join(profile_raw.find_all("h5", string=["Mod watch", "Game watch", "Group watch", "Engine watch"])[0].parent.span.a["href"])
        
        try:
            share = profile_raw.find("h5", string="Share").parent.span.find_all("a")
            self.share = {
                "reddit": share[0]["href"],
                "mail": share[1]["href"],
                "twitter": share[2]["href"],
                "facebook": share[3]["href"]
            }
        except AttributeError:
            self.share = None

        if page_type in [SearchCategory.developers, SearchCategory.groups]:
            self.private = profile_raw.find("h5", string="Privacy").parent.span.string.strip() != "Public"

            membership = profile_raw.find("h5", string="Subscription").parent.span.string.strip()
            if membership == "Open to all members":
                self.membership = Membership(3)
            elif membership == "Must apply to join":
                self.membership = Membership(2)
            else:
                self.membership = Membership(1)

        if page_type in [SearchCategory.games, SearchCategory.mods, SearchCategory.addons]:
            self.icon = profile_raw.find("h5", string="Icon").parent.span.img["src"]

        if page_type in [SearchCategory.games, SearchCategory.mods, SearchCategory.engines, SearchCategory.addons]:
            people = profile_raw.find_all("h5", string=["Developer", "Publisher", "Developer & Publisher","Creator", "Company"])
            self.developers = {x.string.lower() : Thumbnail(url=x.parent.a["href"], name=x.parent.a.string, type=ThumbnailType.team if x.string != creator else ThumbnailType.team) for x in people}            

            try:
                d = profile_raw.find("h5", string="Release date").parent.span.time["datetime"]
                self.release = get_date(d)
            except KeyError:
                LOGGER.info("%s %s has not been released", page_type.name, _name)
                self.release = False

        if page_type != SearchCategory.groups:
            try:
                self.homepage =  profile_raw.find("h5", string="Homepage").parent.span.a["href"]
            except AttributeError:
                LOGGER.info("%s %s has no homepage", page_type.name, _name)

        if page_type in [SearchCategory.games, SearchCategory.addons]:
            engine = profile_raw.find("h5", string="Engine")
            url = engine.parent.span.a["href"]
            name = engine.parent.span.a.string
            self.engine = Thumbnail(url=url, name=name, type=ThumbnailType.engine)

        if page_type == SearchCategory.mods:
            game = profile_raw.find("h5", string="Game")
            url = game.parent.span.a["href"]
            name = game.parent.span.a.string
            self.game = Thumbnail(url=url, name=name, type=ThumbnailType.game)

        if page_type == SearchCategory.engines:
            self.license = License(int(profile_raw.find("h5", string="Licence").parent.span.a["href"][-1]))

        if page_type in [SearchCategory.games, SearchCategory.engines, SearchCategory.addons]:
            platforms = profile_raw.find("h5", string="Platforms").parent.span.span.find_all("a")
            self.platforms = [Thumbnail(name=x.string, url=x["href"], type=ThumbnailType.platform) for x in platforms]

    def __repr__(self):
        return f"<Profile type={self.type.name}>"

class Style:
    def __init__(self, html):
        titles = ("Theme", "Genre", "Players")

        misc = html.find_all("h5")
        styles = {style.string.lower() : re.findall(r"(\d*)$", style.parent.a["href"])[0] for style in misc if style.string in titles}

        self.theme = Theme(int(styles["theme"]))
        self.genre = Genre(int(styles["genre"]))
        self.players = PlayerStyle(int(styles["theme"])) 

        try:
            self.scope = html.find("h5", string="Project").parent.a["href"][-1]
        except AttributeError:
            self.scope = None

        try:
            self.boxart = html.find("h5", string="Boxart").parent.span.a.img["src"]
        except AttributeError:
            self.boxart = None

    def __repr__(self):
        return f"<Style genre={self.genre.name} theme={self.theme.name} players={str(self.players)}>"

class Thumbnail:
    def __init__(self, **attrs):
        self.url = join(attrs.get("url"))
        self.name = attrs.get("name")
        self.image = attrs.get("image", None)
        self.type = attrs.get("type")

    def __repr__(self):
        return f"<Thumbnail name={self.name} type={self.type.name}>"

    def parse(self):
        return getattr(sys.modules["moddb"], self.type.name.title())(soup(self.url))

class Comment:
    def __init__(self, html):
        author = html.find("a", class_="avatar")
        self.id = html["id"]
        self.author = Thumbnail(name=author["title"], url=author["href"], image=author.img["src"], type=ThumbnailType.user)
        self.date = get_date(html.find("time")["datetime"])
        actions = html.find("span", class_="actions")

        position = html["class"] 
        if "reply1" in position:
            self.position = 1
        elif "reply2" in position:
            self.position = 2
        else:
            self.position = 0
        self.children = []
        self.content = html.find("div", class_="comment").p.string


        try:
            karma = actions.span.string
            self.karma = int(re.findall(r"[+-]?\d", karma)[0].replace(",", ""))
            self.upvote = actions.find_all("a")[1]["href"]
            self.downvote = actions.find_all("a")[2]["href"]
            self.approved = True
        except AttributeError:
            self.karma = 0
            self.upvote = None
            self.downvote = None
            self.approved = False
        except IndexError:
            self.downvote = None
            self.approved = True

    def __repr__(self):
        return f"<Comment author={self.author.name} position={self.position} approved={self.approved}>"

class Review:
    def __init__(self, **attrs):
        text = attrs.get("text")
        if text:
            self.text = text.text
        else:
            self.text = None

        review = attrs.get("review")
        self.rating = int(review.span.string)

        author = review.div.a
        self.author = Thumbnail(url=author["href"], name=author.string.split(" ")[0], type=ThumbnailType.user)
        self.date = get_date(review.div.span.time["datetime"])

    def __repr__(self):
        return f"<Review author={self.author.name} rating={self.rating}>"

class UserProfile:
    def __init__(self, html):
        profile_raw = html.find("span", string="Profile").parent.parent.parent.find("div", class_="table tablemenu")
        level_raw = profile_raw.find("h5", string="Level").parent.span.div
        name = html.find("meta", property="og:title")["content"]

        self.level = int(level_raw.find("span", class_="level").string)
        self.progress = float("0." + level_raw.find("span", class_="info").strong.string.replace("%", ""))
        self.title = level_raw.find("span", class_="info").a.string

        self.avatar = profile_raw.find("div", class_="avatarinfo").img["src"]
        self.online = bool(profile_raw.find("h5", string="Status"))
        last_online = profile_raw.find("h5", string="Last Online")
        self.last_online = get_date(last_online.parent.span.time["datetime"]) if last_online else None

        try:
            self.gender = profile_raw.find("h5", string="Gender").parent.span.string.strip()
        except AttributeError:
            LOGGER.info("User %s has not publicized their gender", name)
            self.gender = None        

        self.country = profile_raw.find("h5", string="Country").parent.span.string.strip()
        self.follow = join(profile_raw.find("h5", string="Member watch").parent.span.a["href"])

    def __repr__(self):
        return f"<Profile type=user>"

class UserStatistics:
    def __init__(self, html):
        def get(parent):
            return parent.a.string.strip() if parent.a else parent.span.string.strip()

        name = html.find("meta", property="og:title")["content"]
        misc = html.find_all("h5", string=("Watchers", "Activity Points", "Comments", "Tags", "Site visits"))
        self.__dict__.update({stat.string.lower() : int(normalize(get(stat.parent))) for stat in misc})

        visits = normalize(html.find("h5", string="Visitors").parent.a.string)
        self.visits, self.today = get_views(visits)

        self.time = html.find("h5", string="Time Online").parent.span.string.strip()

        try:
            rank = normalize(html.find("h5", string="Rank").parent.span.string).split("of")
            self.rank = int(rank[0].replace(",", ""))
            self.total = int(rank[1].replace(",", ""))
        except AttributeError:
            self.rank = 0
            self.total = 0
            LOGGER.info("User %s has no rank", name)

    def __repr__(self):
        return f"<Statistics rank={self.rank}/{self.total}>"
