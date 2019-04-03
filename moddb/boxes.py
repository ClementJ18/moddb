from .enums import ThumbnailType, SearchCategory, Membership, Licence, Genre, Theme, \
                   PlayerStyle, Scope, ArticleCategory, HardwareCategory, Status, \
                   SoftwareCategory, AddonCategory, GroupCategory, TeamCategory
from .utils import get_date, get_page, get_views, join, normalize, LOGGER, time_mapping, \
                   get_type_from, concat_docs

import re
import sys
import datetime
from typing import List, Any

__all__ = ['Statistics', 'Profile', 'Style', 'Thumbnail', 'Comment', 'CommentList', 'MemberProfile', 
           'MemberStatistics', 'PlatformStatistics', 'PartialArticle', 'Option']

class Statistics:
    """The stats box, on pages that have one. This represents total stats and daily stats in one
    neat package.

    Attributes
    ----------
    files : int
        The number of files this page has uploaded
    articles : int
        The number of articles this page has uploaded
    reviews : int
        The number of reviews this page has been given
    watchers : int
        The number of people following this page
    mods : int
        The number of mods this page is related too (only applies to games, members and teams)
    addons : int
        The number of addons this page has uploaded
    members : int
        The number of members a group has (only applies to groups and teams)
    visits : int
        The total number of times this page has been viewed
    today : int
        The number of times this page has been viewed today
    rank : int
        The current rank of the page against all other pages of the same type
    total : int
        The maximum rank number
    updated : datetime.datetime
        The last time this page was updated
    """
    def __init__(self, html):
        misc = html.find_all("h5", string=("Files", "Articles", "Reviews", "Watchers", "Mods", "Addons", "Members"))
        self.__dict__.update({stat.string.lower() : int(normalize(stat.parent.a.string)) for stat in misc})

        visits = normalize(html.find("h5", string="Visits").parent.a.string)
        self.visits, self.today = get_views(visits)

        rank = normalize(html.find("h5", string="Rank").parent.a.string).split("of")
        self.rank = int(rank[0].replace(",", ""))
        self.total = int(rank[1].replace(",", ""))

        try:
            self.updated = get_date(html.find("time", itemprop="dateModified")["datetime"])
        except TypeError:
            self.updated = None

    def __repr__(self):
        return f"<Statistics rank={self.rank}/{self.total}>"

class Profile:
    """The profile object is used for several models and as such attribute vary based on which model
    the profile is attached too. Profiles are only present on Mod, Game, Member, Addon, Engine, Company,
    Hardware, Software and Group pages.
    
    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Attributes
    -----------
    category : Union[AddonCategory, HardwareCategory, SoftwareCategory, TeamCategory, GroupCategory, SearchCategory]
        The category the page falls under within the context of what the page is. E.g the page is an Addon category
        will be an AddonCategory enum. If the category of the page doesn't fall under any of the above mentionned
        the attribute will be of type SearchCategory.
    contact : str
        The url to contact the page owner
    follow : str
        The url to click to follow the mod
    share : dict{str : str}
        A dictionnary of share links with the place they will be shared as the key and the url
        for sharing as the value.
    private : bool
        Exclusive to Group and Team, True if the group is private, else False
    membership : Membership
        Exclusive to Group and Team, represents the join procedure (invitation only, private, public)
    icon : str
        Exclusive to Game, Mod and Addon pages. URL of the icon image
    developers : dict{str : Thumbnail}
        Exclusive to Game, Mods, Engine and Addon pages. Dictionnary of member/team like thumbnails as 
        values and the role of the member/team as the key (creator, publisher, developer, ect...)
    release : datetime.datetime
        Exclusive to Game, Mods, Engine and Addon pages. Datetime object of when the page was
        released, can be None if the page hasn't seen a release yet.
    homepage : str
        Present on all pages but Group pages. URL to the page's homepage. Can be None
    engine : Thumbnail
        Exclusive to Game and Addon pages. Engine like thumbnails representing the engine the addon/game
        was built for.
    game : Thumbnail
        Exclusive to Mod pages. Game like thumbnail representing the game the mod was built for.
    licence : Licence
        Exclusive to Engine and Addon pages. Object representing the licence the engine operates under.
    platforms : List[Thumbnail]
        Exclusive to Game, Engine and Addon pages. List of platform like thumbnails representing
        the plaftorms the software was built for.
    status : Status
        Exclusive to Games, Mods, Addons, Engines, Hardware .Whether the thing is released, unreleased, ect...

    """
    def __init__(self, html):
        try:
            _name = html.find("a", itemprop="mainEntityOfPage").string
        except AttributeError:
            try:
                _name = html.find("span", itemprop="headline").string
            except AttributeError:
                _name = html.find("div", class_="title").h2.a.string
        try:
            url = html.find("meta", property="og:url")["content"]
        except TypeError:
            url = join(html.find("a", string=self.name)["href"])
            
        regex = r"\/([a-z]+)\/"
        matches = re.findall(regex, url)
        matches.reverse()
        page_type = SearchCategory[matches[0] if matches[0].endswith("s") else matches[0]+"s"]
        
        self.category = page_type
        profile_raw = html.find("span", string="Profile").parent.parent.parent.find("div", class_="table tablemenu")
        self.contact = join(html.find("h5", string="Contact").parent.span.a["href"])
        self.follow = join(profile_raw.find_all("h5", string=["Mod watch", "Game watch", "Group watch", "Engine watch", "Hardware watch", "Software watch"])[0].parent.span.a["href"])
        
        try:
            share = profile_raw.find("h5", string="Share").parent.span.find_all("a")
            self.share = {
                "reddit": share[0]["href"],
                "mail": share[1]["href"],
                "twitter": share[2]["href"],
                "facebook": share[3]["href"]
            }
        except (AttributeError, IndexError):
            LOGGER.info("Something funky about share box of %s %s", page_type.name, _name)
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

        if page_type in [SearchCategory.games, SearchCategory.mods, SearchCategory.engines, SearchCategory.addons, SearchCategory.hardwares, SearchCategory.softwares]:
            people = profile_raw.find_all("h5", string=["Developer", "Publisher", "Developer & Publisher","Creator", "Company"])
            self.developers = {x.string.lower() : Thumbnail(url=x.parent.a["href"], name=x.parent.a.string, type=ThumbnailType.team if x.string != "Creator" else ThumbnailType.member) for x in people}            

            try:
                d = profile_raw.find("h5", string="Release date").parent.span.time
                self.release = get_date(d["datetime"])
            except KeyError:
                LOGGER.info("%s %s has not been released", page_type.name, _name)
                self.release = None

            if "Coming" in d.string:
                self.status = Status.coming_soon
            elif "Early" in d.string:
                self.status = Status.early_access
            elif "Released" in d.string:
                self.status = Status.released
            else:
                self.status = Status.unreleased

            if page_type != SearchCategory.mods:
                platforms = profile_raw.find("h5", string="Platforms").parent.span.find_all("a")
                self.platforms = [Thumbnail(name=x.string, url=x["href"], type=ThumbnailType.platform) for x in platforms]

        if page_type != SearchCategory.groups:
            try:
                self.homepage =  html.find("h5", string="Homepage").parent.span.a["href"]
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

        if page_type in [SearchCategory.engines, SearchCategory.addons]:
            self.licence = Licence(int(profile_raw.find("h5", string="Licence").parent.span.a["href"].split("=")[-1]))

        if page_type == SearchCategory.hardwares:
            self.category = HardwareCategory(int(profile_raw.find("h5", string="Category").parent.span.a["href"].split("=")[-1]))

        if page_type == SearchCategory.softwares:
            self.category = SoftwareCategory(int(profile_raw.find("h5", string="Category").parent.span.a["href"].split("=")[-1]))

        if page_type == SearchCategory.addons:
            self.category = AddonCategory(int(profile_raw.find("h5", string="Category").parent.span.a["href"].split("=")[-1]))
        
        if page_type == SearchCategory.developers:
            category = html.find("h3").string.strip().lower()
            try:
                self.category = TeamCategory[category]
            except KeyError:
                self.category = TeamCategory(7)

        if page_type == SearchCategory.groups:
            category = html.find("h3").string.strip().lower().replace(" & ", "_")
            self.category = GroupCategory[category]

    def __repr__(self):
        return f"<Profile category={self.category.name}>"

class Style:
    """Represents semantic information on the page's theme. 
    
    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Attributes
    ----------
    theme : Theme
        fantasy, sci-fi, ect...
    genre : Genre
        fps, rpg, moba, ect...
    players : PlayerStyle
        Singplayer, multiplayer, ect...
    scope : Scope
        Triple A games or indie
    boxart : str
        URL of the boxart for the page.
    """
    def __init__(self, html):
        misc = html.find_all("h5", string=("Theme", "Genre", "Players"))
        styles = {style.string.lower() : re.findall(r"(\d*)$", style.parent.a["href"])[0] for style in misc}

        self.theme = Theme(int(styles["theme"]))
        self.genre = Genre(int(styles["genre"]))
        self.players = PlayerStyle(int(styles["theme"])) 

        try:
            self.scope = Scope(int(html.find("h5", string="Project").parent.a["href"][-1]))
        except AttributeError:
            LOGGER.info("Has no scope")

        try:
            self.boxart = html.find("h5", string="Boxart").parent.span.a.img["src"]
        except AttributeError:
            LOGGER.info("Has no boxart")

    def __repr__(self):
        return f"<Style genre={self.genre.name} theme={self.theme.name} players={str(self.players)}>"

class Thumbnail:
    """Thumbnail objects are minature version of ModDB models. They can be parsed to return the full
    version of the model.
    
    Attributes
    -----------
    url : str
        The url to the full model, mandatory attribute.
    name : str
        The name of the model
    image : str
        The optional thumbnail image of the model
    summary : str
        Optional bit of fluff
    date : datetime.datetime
        A date related to this timestamp if it exists. Can be None
    type : ThumbnailType
        The type of the resource, mandatory attribute

    """
    def __init__(self, **attrs):
        self.url = join(attrs.get("url"))
        self.name = attrs.get("name", None)
        self.image = attrs.get("image", None)
        self.summary = attrs.get("summary", None)
        self.date = attrs.get("date", None)
        self.type = attrs.get("type")

    def __repr__(self):
        return f"<Thumbnail name={self.name} type={self.type.name}>"

    def parse(self) -> Any:
        """Uses the Thumbnail's mandatory attributes to get the full html of the
        model and parse them with the appropriate object.

        Returns
        --------
        Any
            The model that was parsed, can be any model from the list of the ThumbnailType
            enum.
        """
        return getattr(sys.modules["moddb"], self.type.name.title())(get_page(self.url))

@concat_docs
class Update(Thumbnail):
    """An update object. Which is basically just a fancy thumbnail with a couple extra attributes and 
    methods.

    Attributes
    -----------
    updates : List[Thumbnail]
        A list of thumbnail objects of the things thave have been posted (new files, new images)
    """

    def __init__(self, **attrs):
        super().__init__(**attrs)

        self.updates = attrs.get("updates")
        self._unfollow_url = join(attrs.get("unfollow"))
        self._clear_url = join(attrs.get("clear"))
        self._client = attrs.get("client")

    def __repr__(self):
        return f"<Update name={self.name} type={self.type.name} updates={len(self.updates)}>"

    def clear(self):
        """Clears all updates"""
        self._client._request("post", self._clear_url)

    def unfollow(self):
        """Unfollows the update object. This will clear the updates"""
        self._client._request("post", self._unfollow_url)



class Comment:
    """A moddb comment object.
    
    Parameters
    -----------
    html : bs4.Tag
        The html to parse into the object. Must be the exact div of the comment.

    Attributes
    -----------
    id : int
        The ID of the comment
    author : Thumbnail
        A member like thumbnail of the member who posted the comment
    date : datetime.datetime
        Date and time of the comment creation
    position : int
        Ranging from 0-2 represents the nested level of the comment.
    children : int
        Comment object replying directly to this one. If the comment is
        parsed on its own it will be null. It is only populated if originating
        from a CommentList
    content : str
        Text of the comment can be none if the comment only contains embeds
    embeds : list
        List of urls that have been embeded
    karma : int
        The current karma count
    upvote : str
        Link to upvote the comment
    downvote : str
        Link to downvote the comment
    approved : bool
        Whether or not the comment is still waiting for admin approval and is visible to the guest members
    developer : bool
        Whether or not the comment was posted one of the page creators
    staff : bool
        Wether or not the comment was posted by one of moddb's staff members
    subscriber : bool
        Whether or not the comment was posted by a moddb subscriber
    guest : bool
        Whether or not the comment was posted by a guest user
    location : Thumbnail
        Thumbnail of the place the comment is, only available when getting comments from get_member_comments. This
        thumbnail does not guarantee that you will find the comment if you parse it, since the url does not
        contain the page number.
    """
    def __init__(self, html):
        author = html.find("a", class_="avatar")
        self.id = int(html["id"])
        self.author = Thumbnail(name=author["title"], url=author["href"], image=author.img["src"], type=ThumbnailType.member)
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

        try:
            self.content = html.find("div", class_="comment").text
        except AttributeError:
            LOGGER.info("Comment %s by %s has no content, likely embed", self.id, self.author.name)
            self.content = None

        try:
            karma = actions.span.string
            self.karma = int(re.findall(r"[+-]?\d", karma)[0].replace(",", ""))
            self.upvote = join(actions.find_all("a")[1]["href"])
            self.downvote = join(actions.find_all("a")[2]["href"])
            self.approved = True
        except AttributeError:
            self.karma = 0
            self.upvote = None
            self.downvote = None
            self.approved = False
        except IndexError:
            self.downvote = None
            self.approved = True

        self.developer = bool(html.find("span", class_="developer"))
        self.staff = bool(html.find("span", class_="staff"))
        self.subscriber = bool(html.find("span", class_="subscriber"))
        self.guest = self.author.name.lower() == "guest"

        self.embeds = [x["src"] for x in html.find_all("iframe")]

        self.location = html.find("a", class_="related")
        if self.location is not None:
            url = join(self.location["href"])
            page_type = get_type_from(url)
            self.location = Thumbnail(name=self.location.string, url=url, type=page_type)

    def __repr__(self):
        return f"<Comment author={self.author.name} position={self.position} approved={self.approved}>"

class CommentList(list):
    """Represents a list of comments. Inherits and works like a regular list but has an 
    additional method called 'flatten' used to get all the nested children in a list"""

    def flatten(self) -> List[Comment]:
        """Returns a 'flattened' list of comments where children of comments are added right
        after the parent comment so:
        
        [ Comment1 ]
            ├── Comment2\n
                ├── Comment3\n
                └── Comment4\n
            └── Comment5

        would become:
        
        [Comment1, Comment2, Comment3, Comment4, Comment5]
        
        Returns
        --------
        list[Comment]
            The flattened list of comments
        """
        top_list = []
        for comment in super().__iter__():
            top_list.append(comment)
            for child in comment.children:
                top_list.append(child)
                top_list.extend(child.children)

        return top_list

class MemberProfile:
    """Member profiles are separate entities because they share nothing with the other profile boxes. Where as all
    other profile boxes share at least 4 attributes, a member shares none.

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Attributes
    -----------
    name : str
        Name of the member
    level : int
        Current level
    progress : float
        Percentage progress to next level
    title : str
        Member title
    avatar : str
        Url of the member avatar
    online : bool
        Whether or not the member is currently online
    last_online :  datetime.datetime
        None if the member is currently online, datetime the user was last seen online
    gender : str
        Gender of the member, can be None
    homepage : str
        URL of the member's homepage
    country : str
        The member's chosen country
    follow : str
        Link to follow a member
    """
    def __init__(self, html):
        profile_raw = html.find("span", string="Profile").parent.parent.parent.find("div", class_="table tablemenu")
        level_raw = profile_raw.find("h5", string="Level").parent.span.div
        self.name = html.find("meta", property="og:title")["content"]

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
            LOGGER.info("Member %s has not publicized their gender", self.name)
            self.gender = None  

        try:
            self.homepage =  html.find("h5", string="Homepage").parent.span.a["href"]
        except AttributeError:
            self.homepage = None
            LOGGER.info("Member %s has no homepage", self.name)      

        self.country = profile_raw.find("h5", string="Country").parent.span.string.strip()

        try:
            self.follow = join(profile_raw.find("h5", string="Member watch").parent.span.a["href"])
        except AttributeError:
            LOGGER.info("Can't watch yourself, narcissist...")
            self.follow = None

    def __repr__(self):
        return f"<MemberProfile name={self.name}>"

class MemberStatistics:
    """Similarly, a member statistics shared no common ground with other stats and therefore there was a 
    need for a separate object.

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Attributes
    -----------
    watchers : int
        How many members are following this member
    acivity_points : int
        Activity points
    comments : int
        How many comments the member has made
    tags : int
        How many tags the member has created
    visits : int
        How many people have viewed this page
    site_visits : int
        How many time this user has visited the site
    today : int
        How many people have viewed this page today
    time : int
        How many seconds the member has spent online
    rank : int
        The member's current rank (compared to other members)
    total : int
        the maximum rank
    """
    def __init__(self, html):
        def get(parent):
            return parent.a.string.strip() if parent.a else parent.span.string.strip()

        name = html.find("meta", property="og:title")["content"]
        misc = html.find_all("h5", string=("Watchers", "Activity Points", "Comments", "Tags", "Site visits"))
        self.__dict__.update({stat.string.lower().replace(" ", "_") : int(normalize(get(stat.parent))) for stat in misc})

        visits = normalize(html.find("h5", string="Visitors").parent.a.string)
        self.visits, self.today = get_views(visits)

        time, mapping = html.find("h5", string="Time Online").parent.span.string.strip().split(" ")
        self.time = time_mapping[mapping.replace('s', '')] * int(time)

        try:
            rank = normalize(html.find("h5", string="Rank").parent.span.string).split("of")
            self.rank = int(rank[0].replace(",", ""))
            self.total = int(rank[1].replace(",", ""))
        except AttributeError:
            self.rank = 0
            self.total = 0
            LOGGER.info("Member %s has no rank", name)

    def __repr__(self):
        return f"<MemberStatistics rank={self.rank}/{self.total}>"

class PlatformStatistics:
    """Stats for platform pages.
    
    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Attributes
    -----------
    hardware : int
        Number of harware created for this platform
    software : int
        Number of software created for this platform
    engines : int
        Number of engines created for this platform
    games : int
        Number of games created for this platform
    mods : int
        Number of mods created for this platform
    """
    def __init__(self, html):
        headings = ("Hardware", "Software", "Engines", "Games", "Mods")
        html_headings = html.find_all("h5", string=headings)
        self.__dict__.update({headings[html_headings.index(x)].lower() : int(normalize(x.parent.span.a.string)) for x in html_headings})

    def __repr__(self):
        return f"<PlatformStatistics>"

class PartialArticle:
    """A partial article is an article object missing attributes due to being parsed from the front page
    intead of from the article page itself. In general, it' is simple enough for previewing the article
    but if you need a full article with comments, profile, ect... Then parse it with the method

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Attributes
    -----------
    name : str
        Name of the articles
    url : str
        Link to the article
    date : datetime.datetime
        Date the article was published
    type : ArticleCategory
        Type of the article
    content : str
        html of the article content
    plaintext : str 
        plaintext of the article content (without html)
    """
    def __init__(self, html):
        meta_raw = html.find("div", class_="row rowcontent rownoimage clear")

        self.name = meta_raw.h4.a.string
        self.url = join(meta_raw.h4.a["href"])
        self.date = get_date(meta_raw.find("time")["datetime"])
        try:
            self.type = ArticleCategory[meta_raw.find("span", class_="subheading").text.strip().split(" ")[0].lower()]
        except KeyError:
            self.type = ArticleCategory.news

        content = html.find("div", class_="row rowcontent rowcontentnext clear")
        self.content = str(content)
        self.plaintext = content.text

    def __repr__(self):
        return f"<PartialArticle title={self.name}>"

    def get_article(self) -> 'Article':
        """Returns the full article object of this article.

        Returns
        --------
        Article
            The complete article object
        """
        return getattr(sys.modules["moddb"], "Article")(get_page(self.url))

class Option:
    """Represents one of the choice from the poll they are attached to, should not be created
    manually, prefer relying on the Poll.

    Attributes
    -----------
    id : int
        The id of the option, can be None and will be None in most cases.
    text : str
        The option's text 
    votes : int
        The number of votes that have been cast on this option
    percent : int
        The percent of all votes that have been cast on this option
    """
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.text = kwargs.get("text")
        self.votes = kwargs.get("votes")
        self.percent = kwargs.get("percent")

    def __repr__(self):
        return f"<Option text={self.text}>"
