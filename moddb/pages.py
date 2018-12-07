from .boxes import *
from .enums import ThumbnailType, SearchCategory, FileCategory, MediaCategory, ArticleType
from .utils import soup, join, LOGGER, get_type, get_date, get_views

import re

__all__ = ['Mod', 'Game', 'Engine', 'File', 'Addon', 'Media', 'Article',
           'Team', 'Group', 'Job', 'Blog', 'User', 'PartialArticle']

class Base:
    def _get_comments(self, html):
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

    def get_comments(self, index=1):
        return self._get_comments(soup(f"{self.url}/page/{index}"))

class Page(Base):
    def __init__(self, html, page_type):
        self.name = html.find("a", itemprop="mainEntityOfPage").string

        #boxes
        self.profile = Profile(html)
        self.statistics = Statistics(html)
        if page_type != SearchCategory.engines:
            self.style = Style(html)

        #thumbnails
        self.suggestions = self._get_suggestions(html)
        self.files = self._get_files(html)

        articles_raw = None
        try:
            string = "Articles" if page_type == SearchCategory.mods else "Related Articles"
            articles_raw = html.find("span", string=string).parent.parent.parent.find("div", class_="table")
            thumbnails = articles_raw.find_all("div", class_="row rowcontent clear")
            self.articles = [Thumbnail(name=x.a["title"], url= join(x.a["href"]), image=x.a.img["src"], type=ThumbnailType.article) for x in thumbnails]
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
        self.imagebox = [Thumbnail(name=x.a["title"], url=join(x.a["href"]), image=x.a.img["src"], type=ThumbnailType(get_type(x.a.img))) for x in imagebox]
        
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
        

    def _get_suggestions(self, html):
        suggestions_raw = html.find("span", string="You may also like").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)
        suggestions = []
        for x in suggestions_raw:
            try:
                link = x.find("a", class_="image")
                suggestion_type = link["href"].split("/")[1].replace("s", "")
                suggestion = Thumbnail(name=link["title"], url=join(link["href"]), image=link.img["src"], type=ThumbnailType[suggestion_type])
                suggestions.append(suggestion)
            except (AttributeError, TypeError):
                pass

        return suggestions

    def _get_files(self, html):
        files_raw = html.find(string="Files").parent.parent.parent.parent.find_all(class_="row rowcontent clear")
        files = []
        for x in files_raw:
            link = x.find("div", class_="content").h4.a
            image_url = link.parent.parent.parent.find("img")["src"]
            file = Thumbnail(name=link.string, url=join(link["href"]), image=image_url, type=ThumbnailType.file)
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
            thumbnail = Thumbnail(name=obj.a["title"], url=join(obj.a["href"]), image=obj.a.img["src"], type=object_type)
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

    def _get_games(self, html):
        games_raw = html.find(string="Games").parent.parent.parent.parent.find_all(class_="row rowcontent clear")
        games = []
        for x in games_raw:
            link = x.find("div", class_="content").h4.a
            image_url = link.parent.parent.parent.find("img")["src"]
            game = Thumbnail(name=link.string, url=join(link["href"]), image=image_url, type=ThumbnailType.game)
            games.append(game)

        return games

    def get_games(self, index=1):
        return self._get(f"{self.url}/games/page/{index}", ThumbnailType.game)

class File(Base):
    def __init__(self, html):
        files_headings = ("Filename", "Size", "MD5 Hash")
        info = html.find("div", class_="table tablemenu")
        t = [t for t in info.find_all("h5") if t.string in files_headings]

        file = {x.string.lower() : x.parent.span.string.strip() for x in info.find_all("h5") if x.string in files_headings}
        self.downloads = info.find("h5", string="Downloads").parent.a.string
        self.hash = file["md5 hash"]
        self.name = file["filename"]
        self.comments = self._get_comments(html)

        self.size = int(re.sub(r"[(),bytes]", "", file["size"].split(" ")[1]))
        self.today = int(re.sub(r"[(),today]", "", self.downloads.split(" ")[1]))
        self.downloads = int(self.downloads.split(" ")[0].replace(",", ""))

        self.type = FileCategory(int(info.find("h5", string="Category").parent.a["href"][-1]))
        
        uploader = info.find("h5", string="Uploader").parent.a
        self.author = Thumbnail(url=join(uploader["href"]), name=uploader.string, type=ThumbnailType.user)

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

        self.date = get_date(raw_media["date"].span.time["datetime"])
        url = raw_media["by"].span.a["href"]
        name = raw_media["by"].span.a.string.strip()

        self.author = Thumbnail(url=url, name=name, type=ThumbnailType.user)
        self.comments = self._get_comments(html)

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
        self.name = html.find("meta", property="og:title")["content"]
        self.url = html.find("meta", property="og:url")["content"]


    def __repr__(self):
        return f"<Media name={self.name} type={self.type.name}>"

#article, blog, headlines
class Article(Base):
    def __init__(self, html):
        raw_type = html.find("h5", string="Browse").parent.span.a.string
        self.type = ArticleType[raw_type.lower()]
        self.comments = self._get_comments(html)
        self.title = html.find("span", itemprop="headline").string

        try:
            raw = html.find("span", string=raw_type[0:-1]).parent.parent.parent.find("div", class_="table tablemenu")
        except AttributeError:
            raw = html.find("span", string=raw_type).parent.parent.parent.find("div", class_="table tablemenu")

        self.profile = Profile(html)

        try:
            self.tags = {x.string : x["href"] for x in raw.find("h5", string="Tags").parent.span.find_all("a") if x is not None}
        except AttributeError:
            self.tags = {}
            LOGGER.info("Article %s has no tags", self.title)

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
        self.author = Thumbnail(name=author.string, url=join(author["href"]), type=ThumbnailType.user)

        self.date = get_date(html.find("time", itemprop="datePublished")["datetime"])
        self.html = str(html.find("div", itemprop="articleBody"))
        self.plaintext = html.find("div", itemprop="articleBody").text

    def __repr__(self):
        return f"<Article title={self.title} type={self.type.name}>"

class Team:
    pass

class Group:
    pass

class Job:
    pass

class Blog(Base):
    def __init__(self, **attrs):
        heading = attrs.get("heading")
        text = attrs.get("text")

        author = heading.find("span", class_="subheading").a
        self.author = Thumbnail(url=join(author["href"]), name=author.string, type=ThumbnailType.user)

        self.date = get_date(heading.find("span", class_="date").time["datetime"])

        title = heading.div.h4.a
        self.title = title.string
        self.url = join(title["href"])

        self.html = str(text.content)
        self.plaintext = text.text

    def __repr__(self):
        return f"<Blog title={self.title}>"


class User(Page):
    def __init__(self, html):
        self.profile = UserProfile(html)

        self.stats = UserStatistics(html)

        self.url = html.find("meta", property="og:url")["content"]
        self.name = html.find("meta", property="og:title")["content"]
        self.description = html.find("div", id="profiledescription").p.string

        try:
            groups_raw = html.find("span", string="Groups").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[:-2]
            self.groups = [Thumbnail(name=div.a["title"], url=join(div.a["href"]), type=ThumbnailType.group) for div in groups_raw]
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
            self.blogs = [Thumbnail(name=blog.a["title"], url=join(blog.a["href"]), type=ThumbnailType.blog) for blog in blogs_raw[:-2]]
        except (TypeError, AttributeError):
            self.blogs = []
            LOGGER.info("User %s has no blog suggestions", self.name)

        try:
            imagebox = html.find("ul", id="imagebox").find_all("li")[1:-2]
            self.imagebox = [Thumbnail(name=x.a["title"], url=join(x.a["href"]), image=x.a.img["src"], type=ThumbnailType(get_type(x.a.img))) for x in imagebox if x.a]
        except AttributeError:
            self.imagebox = []
            LOGGER.info("User %s has no imagebox", self.name)

        try:
            friends = html.find("div", class_="table tablerelated").find_all("div", recursive=False)[1:]
            self.friends = [Thumbnail(name=friend.a["title"], url=join(friend.a["href"]), type=ThumbnailType.user) for friend in friends]
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

        self.title = meta_raw.h4.a.string
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
        return f"<PartialArticle title={self.title}>"

    def get_article(self):
        return Article(soup(self.url))
