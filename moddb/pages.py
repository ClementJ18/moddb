from .boxes import *
from .enums import *
from .utils import soup, join, LOGGER, get_type, get_date, get_views

import re
import bs4
from typing import Tuple


__all__ = ['Mod', 'Game', 'Engine', 'File', 'Addon', 'Media', 'Article',
           'Team', 'Group', 'Job', 'Blog', 'User', 'PartialArticle']

class Base:
    """An abstract class that implements the methods used on nearly every page. In addition, it implements
    some shared hidden methods."""
    
    def _get_comments(self, html : bs4.BeautifulSoup) -> CommentsList:
        """Extracts the comments from an html page and adds them to a CommentsList. In addition
        this command also adds them to the comments children as need be.

        Paramater
        ----------
        html : bs4.BeautifulSoup
            The html 
        """
        comments_raw = html.find("div", class_="table tablecomments").find_all("div", recursive=False)
        comments = CommentsList()
        for raw in comments_raw:
            if "row" in raw.get("class", None):
                comment = Comment(raw)
                if comment.position == 1:
                    comments[-1].children.append(comment)
                elif comment.position == 2:
                    comments[-1].children[-1].children.append(comment)
                else:
                    comments.append(comment)
                    
        return comments

    def _get_blogs(self, index):
        html = soup(f"{self.url}/blogs/page/{index}")
        table = html.find("div", id="articlesbrowse").find("div", class_="table")
        if len(table["class"]) > 1:
            return []

        raw_blogs = table.find_all("div", recursive=False)[2:]
        blogs = []
        e = 0
        for _ in range(len(raw_blogs)):
            try:
                heading = raw_blogs[e]
            except IndexError:
                break

            try:
                text = raw_blogs[e+1]
            except IndexError:
                text = {"class": "None"}

            blog_obj = Blog(heading=heading, text=text)
            blogs.append(blog_obj)
            e += 2

        return blogs

    def _get_suggestions(self, html):
        suggestions_raw = html.find("span", string="You may also like").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)
        suggestions = []
        for x in suggestions_raw:
            try:
                link = x.find("a", class_="image")
                suggestion_type = link["href"].split("/")[1].replace("s", "")
                suggestion = Thumbnail(name=link["title"], url=link["href"], image=link.img["src"], type=ThumbnailType[suggestion_type])
                suggestions.append(suggestion)
            except (AttributeError, TypeError):
                pass

        return suggestions

    def _get_games(self, html):
        games_raw = html.find(string="Games").parent.parent.parent.parent.find_all(class_="row rowcontent clear")
        games = []
        for x in games_raw:
            link = x.find("div", class_="content").h4.a
            image_url = link.parent.parent.parent.find("img")["src"]
            game = Thumbnail(name=link.string, url=link["href"], image=image_url, type=ThumbnailType.game)
            games.append(game)

        return games

    def get_comments(self, index=1):
        return self._get_comments(soup(f"{self.url}/page/{index}"))

class Page(Base):
    def __init__(self, html, page_type):
        self.id = int(re.search(r"siteareaid=(\d*)", html.find("a", string="Follow")["href"])[1])
        self.name = html.find("a", itemprop="mainEntityOfPage").string

        #boxes
        self.profile = Profile(html)
        self.statistics = Statistics(html)
        if page_type != SearchCategory.engines:
            self.style = Style(html)

        #thumbnails
        self.suggestions = self._get_suggestions(html)
        try:
            self.files = self._get_files(html)
        except AttributeError:
            LOGGER.info("%s %s has no files", self.profile.type.name, self.name)
            self.files = []

        articles_raw = None
        try:
            string = "Articles" if page_type == SearchCategory.mods else "Related Articles"
            articles_raw = html.find("span", string=string).parent.parent.parent.find("div", class_="table")
            thumbnails = articles_raw.find_all("div", class_="row rowcontent clear")
            self.articles = [Thumbnail(name=x.a["title"], url=x.a["href"], image=x.a.img["src"] if x.a.img else None, type=ThumbnailType.article) for x in thumbnails]
        except AttributeError:
            LOGGER.info("%s %s has no article suggestions", self.profile.type.name, self.name)
            self.articles = []

        #main page article
        if articles_raw:
            self.article = PartialArticle(articles_raw)
        else:
            self.article = None
            LOGGER.info("%s %s has no front page article", self.profile.type.name, self.name)

        try:
            self.comments = self._get_comments(html)
        except AttributeError:
            self.comments = []
            LOGGER.info("%s %s has no comments", self.profile.type.name, self.name)

        raw_tags = html.find("form", attrs={"name": "tagsform"}).find_all("a")
        self.tags = {x.string : join(x["href"]) for x in raw_tags if x.string is not None}

        #imagebox
        imagebox = html.find("ul", id="imagebox").find_all("li")[1:-2]
        self.imagebox = [Thumbnail(name=x.a["title"], url=x.a["href"], image=x.a.img["src"], type=ThumbnailType(get_type(x.a.img))) for x in imagebox]
        
        #misc
        try:
            self.embed = html.find("input", type="text", class_="text textembed")["value"]
        except TypeError:
            self.embed = str(html.find_all("textarea")[1].a)

        self.url = html.find("meta", property="og:url")["content"]
        try:
            self.rating = float(html.find("div", class_="score").find("meta", itemprop="ratingValue")["content"])
        except AttributeError:
            self.rating = 0.0
            LOGGER.info("%s %s is not rated", self.profile.type.name, self.name)

    def _get_files(self, html):
        files_raw = html.find(string="Files").parent.parent.parent.parent.find_all(class_="row rowcontent clear")
        files = []
        for x in files_raw:
            link = x.find("div", class_="content").h4.a
            image_url = link.parent.parent.parent.find("img")["src"]
            file = Thumbnail(name=link.string, url=link["href"], image=image_url, type=ThumbnailType.file)
            files.append(file)

        return files

    def get_reviews(self, index=1):
        html = soup(f"{self.url}/reviews/page/{index}")
        table = html.find("div", id="articlesbrowse").find("div", class_="table")
        if len(table["class"]) > 1:
            return []

        raw_reviews = table.find_all("div", recursive=False)[2:]
        reviews = []
        e = 0
        for _ in range(len(raw_reviews)):
            try:
                review = raw_reviews[e]
            except IndexError:
                break

            try:
                text = raw_reviews[e+1]
            except IndexError:
                text = {"class": "None"}

            if "rowcontentnext" in text["class"]:
                e += 1
                review_obj = Review(review=review, text=text)
            else:
                review_obj = Review(review=review)

            reviews.append(review_obj)
            e += 1

        return reviews

    def _get(self, url, object_type):
        html = soup(url)

        table = html.find("div", class_="table")
        if len(table["class"]) > 1:
            return []

        objects_raw = table.find_all("div", recursive=False)[1:]
        objects = []
        for obj in objects_raw:
            thumbnail = Thumbnail(name=obj.a["title"], url=obj.a["href"], image=obj.a.img["src"], type=object_type)
            objects.append(thumbnail)

        return objects

    def get_articles(self, index=1):
        return self._get(f"{self.url}/articles/page/{index}", ThumbnailType.article)
        
    def get_files(self, index=1):
        return self._get(f"{self.url}/downloads/page/{index}", ThumbnailType.file)

    def get_images(self, index=1):
        pass

    def get_videos(self, index=1):
        pass

    def get_tutorials(self, index=1):
        return self._get(f"{self.url}/tutorials/page/{index}", ThumbnailType.article)

    def get_addons(self, index=1):
        return self._get(f"{self.url}/addons/page/{index}", ThumbnailType.addon)

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}>"

class Mod(Page):
    def __init__(self, html):
        super().__init__(html, SearchCategory.mods)

class Game(Page):
    def __init__(self, html):
        super().__init__(html, SearchCategory.games)

    def get_mods(self, index=1):
        return self._get(f"{self.url}/mods/page/{index}", ThumbnailType.mod)

class Engine(Page):
    def __init__(self, html):
        super().__init__(html, SearchCategory.engines)
        delattr(self, "files")

        self.games = self._get_games(html)

    def get_games(self, index=1):
        return self._get(f"{self.url}/games/page/{index}", ThumbnailType.game)

class File(Base):
    def __init__(self, html):
        self.id = int(re.search(r"siteareaid=(\d*)", html.find("a", string="Follow")["href"])[1])
        files_headings = ("Filename", "Size", "MD5 Hash")
        info = html.find("div", class_="table tablemenu")
        t = [t for t in info.find_all("h5") if t.string in files_headings]

        file = {x.string.lower() : x.parent.span.string.strip() for x in info.find_all("h5") if x.string in files_headings}
        self.downloads = info.find("h5", string="Downloads").parent.a.string
        self.hash = file["md5 hash"]
        self.name = file["filename"]
        try:
            self.comments = self._get_comments(html)
        except AttributeError:
            self.comments = []
            LOGGER.info("File %s has no comments", self.name)

        self.size = int(re.sub(r"[(),bytes]", "", file["size"].split(" ")[1]))
        self.today = int(re.sub(r"[(),today]", "", self.downloads.split(" ")[1]))
        self.downloads = int(self.downloads.split(" ")[0].replace(",", ""))

        self.type = FileCategory(int(info.find("h5", string="Category").parent.a["href"][-1]))
        
        uploader = info.find("h5", string="Uploader").parent.a
        self.author = Thumbnail(url=uploader["href"], name=uploader.string, type=ThumbnailType.user)

        self.date = get_date(info.find("h5", string="Added").parent.span.time["datetime"])
        self.button = info.find("h5", string="Embed Button").parent.span.input["value"]
        self.widget = info.find("h5", string="Embed Widget").parent.span.input["value"]

        self.description = html.find("p", id="downloadsummary").string
        self.preview = html.find_all("img")[0]["src"]
        self.url = html.find("meta", property="og:url")["content"]

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name} type={self.type.name}>"

class Addon(File):
    def __init__(self, html):
        super().__init__(html)

class Media(Base):
    def __init__(self, html):
        media_headings = ("Date", "By", "Duration", "Size", "Views", "Filename")
        raw_media = {media.string.lower() : media.parent for media in html.find_all("h5") if media.string in media_headings}

        self.id = int(re.search(r"siteareaid=(\d*)", html.find("a", string="Follow")["href"])[1])
        self.date = get_date(raw_media["date"].span.time["datetime"])
        self.name = raw_media["by"].span.a.string.strip()

        self.author = Thumbnail(url=url, name=name, type=ThumbnailType.user)
        try:
            self.comments = self._get_comments(html)
        except AttributeError:
            self.comments = []
            LOGGER.info("Media %s has no comments", self.name)

        if "duration" in raw_media:
            duration = raw_media["duration"].span.time.string.strip().split(":")
            self.duration = (int(duration[0]) * 60) + int(duration[1])

        if "size" in raw_media:
            self.size = tuple(raw_media["size"].span.string.strip().split("×"))

        self.views, self.today = get_views(raw_media["views"])

        if "filename" in raw_media:
            self.filename = raw_media["filename"].span.string.strip()

        if "size" in raw_media and "duration" in raw_media:
            self.type = MediaCategory.video
            self.url = html.find("meta", property="og:image")["content"][:-4]
        elif "size" in raw_media:
            self.type = MediaCategory.image
            self.url = html.find("meta", property="og:image")["content"]
        else:
            self.type = MediaCategory.audio
            self.url = html.find("video", id="mediaplayer").find("source")["src"]

        self.description = html.find("meta", {"name":"description"})["content"]


    def __repr__(self):
        return f"<Media name={self.name} type={self.type.name}>"

#article, blog, headlines
class Article(Base):
    def __init__(self, html):
        raw_type = html.find("h5", string="Browse").parent.span.a.string
        self.type = ArticleType[raw_type.lower()]
        self.name = html.find("span", itemprop="headline").string
        self.id = int(re.search(r"siteareaid=(\d*)", html.find("a", string="Follow")["href"])[1])

        try:
            self.comments = self._get_comments(html)
        except AttributeError:
            self.comments = []
            LOGGER.info("Article %s has no comments", self.name)

        try:
            raw = html.find("span", string=raw_type[0:-1]).parent.parent.parent.find("div", class_="table tablemenu")
        except AttributeError:
            raw = html.find("span", string=raw_type).parent.parent.parent.find("div", class_="table tablemenu")

        self.profile = Profile(html)

        try:
            self.tags = {x.string : x["href"] for x in raw.find("h5", string="Tags").parent.span.find_all("a") if x is not None}
        except AttributeError:
            self.tags = {}
            LOGGER.info("Article %s has no tags", self.name)

        self.report = raw.find("h5", string="Report").parent.span.a["href"]
        
        views_raw = raw.find("h5", string="Views").parent.span.a.string
        self.views, self.today = get_views(views_raw)
        share = raw.find("h5", string="Share").parent.span.find_all("a")
        self.share = {
            "reddit": share[0]["href"],
            "mail": share[1]["href"],
            "twitter": share[2]["href"],
            "facebook": share[3]["href"]
        }
        
        self.introduction = html.find("p", itemprop="description").string
        author = html.find("span", itemprop="author").span.a
        self.author = Thumbnail(name=author.string, url=author["href"], type=ThumbnailType.user)

        self.date = get_date(html.find("time", itemprop="datePublished")["datetime"])
        self.html = str(html.find("div", itemprop="articleBody"))
        self.plaintext = html.find("div", itemprop="articleBody").text

    def __repr__(self):
        return f"<Article title={self.name} type={self.type.name}>"

class Group(Base):
    def __init__(self, html):
        self.id = int(re.search(r"siteareaid=(\d*)", html.find("a", string="Follow")["href"])[1])
        self.url = html.find("meta", property="og:url")["content"]
        self.name = html.find("div", class_="title").h2.a.string

        try:
            self.profile = Profile(html)
        except AttributeError:
            LOGGER.info("Entity %s has no profile (private)", self.name)
            self.profile = None

        try:
            self.stats = Statistics(html)
        except AttributeError:
            LOGGER.info("Entity %s has no stats (private)", self.name)
            self.stats = None

        try:
            raw_tags = html.find("form", attrs={"name": "tagsform"}).find_all("a")
            self.tags = {x.string : join(x["href"]) for x in raw_tags if x.string is not None}
        except AttributeError:
            LOGGER.info("Entity %s has no tags (private)", self.name)
            self.tags = {}

        #misc
        try:
            self.embed = html.find("input", type="text", class_="text textembed")["value"]
        except TypeError:
            try:
                self.embed = str(html.find_all("textarea")[1].a)
            except IndexError:
                LOGGER.info("Group %s has no embed", self.name)
                self.embed = None

        try:
            imagebox = html.find("ul", id="imagebox").find_all("li")[1:-2]
            self.imagebox = [Thumbnail(name=x.a["title"], url=x.a["href"], image=x.a.img["src"], type=ThumbnailType(get_type(x.a.img))) for x in imagebox if x.a]
        except AttributeError:
            self.imagebox = []
            LOGGER.info("Group %s has no imagebox", self.name)

        try:
            self.comments = self._get_comments(html)
        except AttributeError:
            self.comments = []
            LOGGER.info("Group %s has no comments", self.name)

        self.suggestions = self._get_suggestions(html)

        try:
            articles_raw = html.find("span", string="Articles").parent.parent.parent.find("div", class_="table")
            thumbnails = articles_raw.find_all("div", class_="row rowcontent clear", recursive=False)
            self.articles = [Thumbnail(name=x.a["title"], url=x.a["href"], image=x.a.img["src"], type=ThumbnailType.article) for x in thumbnails]
        except AttributeError:
            LOGGER.info("Group %s has no article suggestions", self.name)
            self.articles = []

        try:
            self.description = html.find("div", id="profiledescription").text
        except AttributeError:
            self.description = html.find("div", class_="column span-all").find("div", class_="tooltip").parent.text

    def __repr__(self):
        return f"<Group name={self.name}>"

    def get_articles(self, index=1):
        return self._get(f"{self.url}/articles/page/{index}", ThumbnailType.article)

    def get_members(self, index=1):
        return self._get(f"{self.url}/members/page/{index}", ThumbnailType.user)

    def get_files(self, index=1):
        return self._get(f"{self.url}/downloads/page/{index}", ThumbnailType.file)

    def get_images(self, index=1):
        pass

    def get_videos(self, index=1):
        pass

    def get_addons(self, index=1):
        return self._get(f"{self.url}/addons/page/{index}", ThumbnailType.addon)

    def get_blogs(self, index=1):
        return self._get_blogs(index)

class Team(Group):
    def __init__(self, html):
        super().__init__(html)
        try:
            self.games = self._get_games(html)
        except AttributeError:
            LOGGER.info("Group %s has no games", self.name)
            self.games = []

        try:
            self.engines = self._get_engines(html)
        except AttributeError:
            LOGGER.info("Group %s has no engines", self.name)
            self.engines = []

    def _get_engines(self, html):
        engines_raw = html.find(string="Engines").parent.parent.parent.parent.find_all(class_="row rowcontent clear")
        engines = []
        for x in engines_raw:
            link = x.find("div", class_="content").h4.a
            image_url = link.parent.parent.parent.find("img")["src"]
            engine = Thumbnail(name=link.string, url=link["href"], image=image_url, type=ThumbnailType.engine)
            engines.append(engine)

        return engines

class Job:
    def __init__(self, html):
        profile_raw = html.find("span", string="Jobs").parent.parent.parent.find("div", class_="table tablemenu")

        self.id = int(re.search(r"siteareaid=(\d*)", html.find("a", string="Follow")["href"])[1])
        author = profile_raw.find("h5", string="Author").parent.span.a
        self.author = Thumbnail(url=author["href"], name=author.string, type=ThumbnailType.user)

        self.paid = profile_raw.find("h5", string="Paid").parent.a.string == "Yes"

        tags = profile_raw.find("h5", string="Tags").parent.span.find_all("a")
        self.tags = {x.string : join(x["href"]) for x in tags}

        self.skill = JobSkill(int(profile_raw.find("h5", string="Skill").parent.span.a["href"][-1]))

        self.location = profile_raw.find("h5", string="Location").parent.span.string.strip()

        text_raw = html.find("div", id="readarticle")
        self.name = text_raw.find("div", class_="title").find("span", class_="heading").string
        self.text = text_raw.find("div", id="articlecontent").text

        related = html.find("div", class_="tablerelated").find_all("a", class_="image")
        self.related = [Thumbnail(url=x["href"], name=x["title"], type=ThumbnailType.team) for x in related]

class Blog(Base):
    def __init__(self, **attrs):
        self.id = int(re.search(r"siteareaid=(\d*)", html.find("a", string="Follow")["href"])[1])
        heading = attrs.get("heading")
        text = attrs.get("text")

        author = heading.find("span", class_="subheading").a
        self.author = Thumbnail(url=author["href"], name=author.string, type=ThumbnailType.user)

        self.date = get_date(heading.find("span", class_="date").time["datetime"])

        title = heading.div.h4.a
        self.name = title.string
        self.url = join(title["href"])

        self.html = str(text.content)
        self.plaintext = text.text

    def __repr__(self):
        return f"<Blog title={self.name}>"


class User(Page):
    def __init__(self, html):
        self.profile = UserProfile(html)
        self.id = int(re.search(r"siteareaid=(\d*)", html.find("a", string="Follow")["href"])[1])
        self.stats = UserStatistics(html)

        self.url = html.find("meta", property="og:url")["content"]
        self.name = html.find("meta", property="og:title")["content"]
        self.description = html.find("div", id="profiledescription").p.string

        try:
            groups_raw = html.find("span", string="Groups").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[:-2]
            self.groups = [Thumbnail(name=div.a["title"], url=div.a["href"], type=ThumbnailType.group) for div in groups_raw]
        except AttributeError:
            LOGGER.info("User %s doesn't have any groups", self.name)
            self.groups = []

        blogs_raw = html.find("span", string="My Blogs").parent.parent.parent.find("div", class_="table")
        try:
            blogs_raw = blogs_raw.find_all("div", recursive=False)
            self.blog = Blog(heading=blogs_raw.pop(0), text=blogs_raw.pop(0))
        except (TypeError, AttributeError):
            self.blog = None
            LOGGER.info("User %s has no front page blog", self.name)

        try:
            blogs_raw = blogs_raw.find_all("div", recursive=False)
            self.blogs = [Thumbnail(name=blog.a["title"], url=blog.a["href"], type=ThumbnailType.blog) for blog in blogs_raw[:-2]]
        except (TypeError, AttributeError):
            self.blogs = []
            LOGGER.info("User %s has no blog suggestions", self.name)

        try:
            imagebox = html.find("ul", id="imagebox").find_all("li")[1:-2]
            self.imagebox = [Thumbnail(name=x.a["title"], url=x.a["href"], image=x.a.img["src"], type=ThumbnailType(get_type(x.a.img))) for x in imagebox if x.a]
        except AttributeError:
            self.imagebox = []
            LOGGER.info("User %s has no imagebox", self.name)

        try:
            friends = html.find("div", class_="table tablerelated").find_all("div", recursive=False)[1:]
            self.friends = [Thumbnail(name=friend.a["title"], url=friend.a["href"], type=ThumbnailType.user) for friend in friends]
        except AttributeError:
            self.friends = []
            LOGGER.info("User %s has no friends ;(", self.name)

        try:
            self.homepage =  html.find("h5", string="Homepage").parent.span.a["href"]
        except AttributeError:
            self.homepage = None
            LOGGER.info("User %s has no homepage", self.name)

        try:
            self.comments = self._get_comments(html)
        except AttributeError:
            self.comments = []
            LOGGER.info("User %s has no comments", self.name)

    def __repr__(self):
        return f"<User name={self.name} level={self.profile.level}>"

    def get_blogs(self, index=1):
        return self._get_blogs(index)

    def get_user_comments(self, index=1):
        html = soup(f"{self.url}/comments/page/{index}")
        return self._get_comments(html)

    def get_friends(self, index=1):
        return self._get(f"{self.url}/friends/page/{index}", ThumbnailType.user)

    def get_groups(self, index=1):
        return self._get(f"{self.url}/groups/page/{index}", ThumbnailType.group)

    def get_games(self, index=1):
        return self._get(f"{self.url}/games/page/{index}", ThumbnailType.game)

    def get_mods(self, index=1):
        return self._get(f"{self.url}/mods/page/{index}", ThumbnailType.mod)
    

class PartialArticle:
    def __init__(self, html):
        meta_raw = html.find("div", class_="row rowcontent rownoimage clear")

        self.name = meta_raw.h4.a.string
        self.url = join(meta_raw.h4.a["href"])
        self.date = get_date(meta_raw.find("time")["datetime"])
        try:
            self.type = ArticleType[meta_raw.find("span", class_="subheading").text.strip().split(" ")[0].lower()]
        except KeyError:
            self.type = ArticleType.news

        content = html.find("div", class_="row rowcontent rowcontentnext clear")
        self.content = str(content)
        self.plaintext = content.text

    def __repr__(self):
        return f"<PartialArticle title={self.name}>"

    def get_article(self):
        return Article(soup(self.url))

class FrontPage:
    def __init__(self, html):
        articles = html.find("span", string="Latest Articles").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[:-1]
        self.articles = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.article, image=x.a.img["src"]) for x in articles]

        mods = html.find("span", string="Popular Mods").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[1:]
        self.mods = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.mod, image=x.a.img["src"]) for x in mods]

        games = html.find("span", string="Popular Games").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[1:]
        self.games = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.game, image=x.a.img["src"]) for x in games]

        # jobs = html.find("span", string="Jobs").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[1:]
        # self.jobs = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.job) for x in jobs]

        files = html.find("span", string="Popular Files").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[1:]
        self.files = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.file, image=x.a.img["src"]) for x in files]

        self.poll = Poll(html.find("div", class_="poll"))

    def __repr__(self):
        return f"<FrontPage articles={len(self.articles)} mods={len(self.mods)} games={len(self.games)}>"

class Poll(Base):
    def __init__(self, html):
        # self.url = html.form["action"]
        # self.question = html.p.string
        # self.hidden = html.form.input["value"]

        # options = html.form.find_all("div", class_="baroption")
        # self._options = [x.input["value"] for x in options]
        # self.options = [x.label.string for x in options]

        poll = html.find("div", class_="poll")
        self.question = poll.parent.parent.parent.find("div", class_="normalcorner").find("span", class_="heading").string

        author = poll.find("p", class_="question").find("a")
        self.author = Thumbnail(name=author.string, url=author["href"], type=ThumbnailType.user)

        self.total = int(re.search(r"([\d,]*) votes", poll.find("p", class_="question").text)[1].replace(",", ""))

        try:
            self.comments = self._get_comments(html)
        except AttributeError:
            LOGGER.info("Poll %s has no comments", question)
            self.comments = []

        percentage = poll.find_all("div", class_="barouter")
        rest = poll.find_all("p")[1:]

        self.options = []
        for x in range(len(percentage)):
            raw = percentage[x].div.string.replace('%', '').replace('\xa0', '')
            percent = float(f"0.{raw}")
            text = re.sub(r"\([\d,]* votes\)", '', rest[x].text)
            votes = int(re.search(r"([\d,]*) votes", rest[x].span.string)[1].replace(',', ''))
            self.options.append(Option(text=text, votes=votes, percent=percent))

    def __repr__(self):
        return f"<Poll question={self.question}>"

class Option:
    def __init__(self, **kwargs):
        self.text = kwargs.get("text")
        self.votes = kwargs.get("votes")
        self.percent = kwargs.get("percent")

    def vote(self):
        pass

    def __repr__(self):
        return f"<Option text={self.text}>"

class Search:
    """Represents the search you just conducted through the library's search function. Can be used to navigate 
    the search page efficiently.

    Attributes
    -----------
    results : list[moddb.Thumbnail]
        The list of results the search returned

    category : moddb.ThumbnailType
        The type results

    filters : dict{str : moddb.Enum}
        The dict of filters that was used to search for the results

    page_max : int
        The number of pages

    page : int
        The current page, range is 1-page_max included

    query : str
        The text query that was used in the search

    results_max : int
        The total number of results for this search

    """
    def __init__(self, **kwargs):
        self.results = kwargs.get("results")
        self.category = kwargs.get("category")
        self.filters = kwargs.get("filters")
        self.page_max = kwargs.get("page_max")
        self.page = kwargs.get("page")
        self.query = kwargs.get("query")
        self.results_max = kwargs.get("results_max")

    def next_page(self) -> 'Search':
        """Returns a new search object with the next page of results, will raise ValueError 
        if the last page is the current one

        Returns
        --------
        moddb.Search
            The new search objects containing a new set of results.

        Raises
        -------
        ValueError
            There is no next page
        """
        if self.page == self.page_max:
            raise ValueError("Reached last page already")

        self.to_page(self.page+1)

    def previous_page(self) -> 'Search': 
        """Returns a new search object with the previous page of results, will raise 
        ValueError if the first page is the current one

        Returns
        --------
        moddb.Search
            The new search objects containing a new set of results.

        Raises
        -------
        ValueError
            There is no previous page
        """
        if self.page == 1:
            raise ValueError("Reached first page already")

        return self.to_page(self.page-1)

    def to_page(self, page : range(0, 4)) -> 'Search': 
        """Returns a new search object with results to a specific page in the search results 
        allowing for fast navigation. Will raise ValueError if you attempt to navigate out 
        of bounds.
    
        Parameters
        -----------
        page : int
            A page number within the range 1 - page_max inclusive

        Returns
        --------
        moddb.Search
            The new search objects containing a new set of results.

        Raises
        -------
        ValueError
            This page does not exist
        """
        if page < 1 or page > self.page_max:
            raise ValueError(f"Please pick a page between 1 and {self.page_max}")

        return search(self.category, query=self.query, page=page, **self.filters)

    def resort(self, new_sort : Tuple[str, str]) -> 'Search': 
        """Allows you to sort the whole search by a new sorting parameters. Returns a new search object.

        Parameters
        -----------
        new_sort : tuple[str, str]
            The new sorting tuple to check by

        Return
        -------
        moddb.Search
            The new set of results with the updated sort order
        """
        return search(self.category, query=self.query, page=1, sort=new_sort, **self.filters)

    def __repr__(self):
        return f"<Search results={len(self.results)}/{self.results_max}, category={self.category.name} pages={self.page}/{self.page_max}>"

