from .boxes import *

class Game:
    pass

class Mod:
    def __init__(self, **attrs):
        for key, value in attrs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Mod name={self.name}>"

    @classmethod
    def parse(cls, html):
        mod = {}

        mod["profile"] = Profile.parse(html)
        mod["statistics"] = Statistics.parse(html)
        mod["style"] = Style.parse(html)

        raw_tags = html.find("span", string="Tags").parent.parent.parent.find("form", attrs={"name": "tagsform"}).find_all("div")
        mod["tags"] = {tag.find("a").string : join(tag.find("a")["href"]) for tag in raw_tags}

        mod["name"] = html.find("a", itemprop="mainEntityOfPage").string

        suggestions_raw = html.find(string="You may also like").parent.parent.parent.parent.find_all(class_="row clear")
        mod["suggestions"] = []
        for x in suggestions_raw:
            link = x.find("a",class_="heading")
            image_url = link.parent.parent.find("img")["src"]
            suggestion = Thumbnail(name=link.string, url=join(link["href"]), image=image_url, type=ThumbnailType.mod)
            mod["suggestions"].append(suggestion)

        files_raw = html.find(string="Files").parent.parent.parent.parent.find_all(class_="row rowcontent clear")
        mod["files"] = []
        for x in files_raw:
            link = x.find("div", class_="content").h4.a
            image_url = link.parent.parent.parent.find("img")["src"]
            file = Thumbnail(name=link.string, url=join(link["href"]), image=image_url, type=ThumbnailType.file)
            mod["files"].append(file)

        articles_raw = html.find("span", string="Articles").parent.parent.parent.find("div", class_="inner").div.find("div", class_="table")
        thumbnails = articles_raw.find_all("div", class_="row rowcontent clear")
        mod["articles"] = [Thumbnail(name=x.a["title"], url= join(x.a["href"]), image=x.a.img["src"], type=ThumbnailType.article) for x in thumbnails]
        mod["article"] = PartialArticle.parse(articles_raw)
        mod["description"] = html.find("meta", itemprop="description")["content"]
        mod["profile"] = str(html.find("div", id="profiledescription"))
        mod["url"] = html.find("meta", property="og:url")["content"]

        def get_type(img):
            if img is None:
                return 2
            elif img["src"][-8:-5] == ".mp4":
                return 0
            elif img["src"].endswith(("png", "jpg")):
                return 1

        imagebox = html.find("ul", id="imagebox").find_all("li")[1:-2]
        mod["imagebox"] = [Thumbnail(name=x.a["title"], url=join(x.a["href"]), image=x.a.img["src"], type=ThumbnailType(get_type(x.a.img))) for x in imagebox]

        return cls(**mod)

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

class PartialArticle:
    def __init__(self, **attrs):
        self.type = attrs.get("type")
        self.date = attrs.get("date")
        self.title = attrs.get("title")
        self.content = attrs.get("content")
        self.plaintext = attrs.get("plaintext")
        self.url = attrs.get("url")

    def __repr__(self):
        return f"<PartialArticle title={self.title}>"

    @classmethod
    def parse(cls, html):
        article = {}
        meta_raw = html.find("div", class_="row rowcontent rownoimage clear")

        article["title"] = meta_raw.h4.a.string
        article["url"] = join(meta_raw.h4.a["href"])
        article["date"] = get_date(meta_raw.find("time")["datetime"])
        article["type"] = ArticleType[meta_raw.find("span", class_="subheading").text.strip().split(" ")[0].lower()]

        content = html.find("div", class_="row rowcontent rowcontentnext clear")
        article["content"] = str(content)
        article["plaintext"] = content.text

        return cls(**article)

    def get_article(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        return Article.parse(soup)

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
