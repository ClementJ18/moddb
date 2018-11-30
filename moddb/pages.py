from .boxes import *

class Game:
    pass

class Mod:
    pass

class File:
    def __init__(self, **attrs):
        self.name = attrs.get("filename")
        self.type = attrs.get("type")
        self.author = attrs.get("author")
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
        return f"<File name={self.name} type={self.type.name}>"

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

        file["type"] = FileCategory(int(info.find("h5", string="Category").parent.a["href"][-1]))
        
        uploader = info.find("h5", string="Uploader").parent.a
        file["author"] = Thumbnail(url=join(uploader["href"]), name=uploader.string, type=ThumbnailType.user)

        file["date"] = get_date(info.find("h5", string="Added").parent.span.time["datetime"])
        file["button"] = info.find("h5", string="Embed Button").parent.span.input["value"]
        file["widget"] = info.find("h5", string="Embed Widget").parent.span.input["value"]

        file["description"] = html.find("p", id="downloadsummary").string
        file["preview"] = html.find_all("img")[0]["src"]

        return cls(**file)

class Media:
    def __init__(self, **attrs):
        self.name = attrs.get("name")
        self.type = attrs.get("type")
        self.url = attrs.get("url")
        self.duration = attrs.get("duration", None)
        self.size = attrs.get("size", None)
        self.views = attrs.get("views")
        self.today = attrs.get("today")
        self.filename = attrs.get("filename", None)
        self.author = attrs.get("author")
        self.description = attrs.get("description")
        self.date = attrs.get("date")

    def __repr__(self):
        return f"<Media name={self.name} type={self.type.name}>"

    @classmethod
    def parse(cls, html):
        media = {}
        media_headings = ("Date", "By", "Duration", "Size", "Views", "Filename")
        raw_media = {media.string.lower() : media.parent for media in html.find_all("h5") if media.string in media_headings}

        media["date"] = get_date(raw_media["date"].span.time["datetime"])
        url = raw_media["by"].span.a["href"]
        name = raw_media["by"].span.a.string.strip()

        media["author"] = Thumbnail(url=url, name=name, type=ThumbnailType.user)

        if "duration" in raw_media:
            duration = raw_media["duration"].span.time.string.strip().split(":")
            media["duration"] = (int(duration[0]) * 60) + int(duration[1])

        if "size" in raw_media:
            media["size"] = tuple(raw_media["size"].span.string.strip().split("×"))

        media["views"], media["today"] = get_views(raw_media["views"])

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
class Article:
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

    def __repr__(self):
        return f"<Article title={self.title} type={self.type.name}>"

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
        article["views"], article["today"] = get_views(views_raw)
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
        article["author"] = Thumbnail(name=author.string, url=join(author["href"]), type=ThumbnailType.user)

        article["date"] = get_date(html.find("time", itemprop="datePublished")["datetime"])
        article["html"] = str(html.find("div", itemprop="articleBody"))
        article["plaintext"] = html.find("div", itemprop="articleBody").text

        return cls(**article)

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

class User:
    pass
