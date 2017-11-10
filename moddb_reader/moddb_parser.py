#!/usr/bin/python3.6
from moddb_objects import *
from bs4 import BeautifulSoup
import requests

class Reader():
    def __init__(self):
        self.url = None
        self.soup = None
        self.rss = None
        self.misc = None

    def _soup_page(self):
        resp = requests.get(self.url)
        soup = BeautifulSoup(resp.text, "html.parser")

        resp = requests.get(self.url.replace("www","rss") + "/articles/feed/rss.xml")
        rss = BeautifulSoup(resp.text, "xml")

        return soup, rss

    def _string_grab(self, string):
        try:
            return [x.parent.a.string for x in self.misc if x.string in string][0]
        except IndexError:
            return None

    def _article_parser(self):
        articles = list()
        article_list = self.rss.find_all("item")
        for article in article_list:
            title = article.title.string
            desc = article.find_all(type="plain")[1].string
            link = article.link.string
            date = article.pubDate.string[:-14]
            articles.append(Article(title, desc, link, date))
        
        return articles

    def _tag_parser(self, raw_tags):
        tags = list()
        for tag in raw_tags:
            name = tag.a.string
            link = self.url + tag.a["href"]
            tags.append(Tag(name, link))

        return tags

    def _count_parser(self, game_bool):
        visits_num = self._string_grab("Visits")
        files_num = self._string_grab("Files")
        articles_num = self._string_grab("Articles")
        reviews_num = self._string_grab("Reviews")
        followers_num = self._string_grab("Watchers")

        if game_bool:
            mods = self._string_grab("Mods")
            return visits_num, followers_num, files_num, articles_num, reviews_num, mods

        return visits_num, followers_num, files_num, articles_num, reviews_num

    def _style_parser(self):
        theme = self._string_grab("Theme")
        genre = self._string_grab("Genre")
        players = self._string_grab("Players")

        return genre, theme, players

    def _suggestion_parser(self):
        suggestions = list()
        suggestions_raw = self.soup.find(string="You may also like").parent.parent.parent.parent.find_all(class_="row clear")
        for x in suggestions_raw:
            link = x.find("a",class_="heading")
            image_url = link.parent.parent.find("img")["src"]
            suggestion = Suggestion(link.string, self.url + link["href"], image_url)
            suggestions.append(suggestion)

        return suggestions

    def _share_parser(self):
        try:
            share_tags = [x.parent.span for x in self.misc if x.string in "Share"][0].find_all("a")
        except IndexError:
            return None

        return Share(share_tags[3]["href"], share_tags[2]["href"], share_tags[1]["href"], share_tags[0]["href"])


    def _basic_game_parser(self):
        engine = [x.parent.a for x in self.misc if x.string == "Engine"][0]
        engine_name = engine.string
        engine_url = "http://www.moddb.com" + engine["href"]
        game_name = self.soup.title.string[:-9].replace(" Windows game", "")
        project = self._string_grab("Project")

        try:
            boxart_url = [x.parent.a["href"] for x in self.misc if x.string == "Boxart"][0]
        except IndexError:
            boxart_url = None

        try:
            follow_url = self.url + [x.parent.a["href"] for x in self.misc if x.string == "Game watch"][0]
        except IndexError:
            follow_url = None

        count = GameCount(*self._count_parser(True))

        return engine_name, engine_url, game_name, project, boxart_url, count, follow_url

    def _basic_mod_parser(self):
        game = [x.parent.a for x in self.misc if x.string == "Game"][0]
        game_name = game.string
        game_url = "http://www.moddb.com" + game["href"]
        mod_name = self.soup.title.string[:-9].replace("for " + game_name, "")
        count = Count(*self._count_parser(False))

        try:
            follow_url = self.url + [x.parent.a["href"] for x in self.misc if x.string == "Mod watch"][0]
        except IndexError:
            follow_url = None

        return game_name, game_url, mod_name, count, follow_url

    def _general_parser(self):
        self.misc = self.soup.find_all("h5")
        desc = self.soup.find("meta", {"name":"description"})["content"]
        publishers = self._string_grab(["Developer & Publisher", "Developer", "Creator"])

        try:
            rating = float(self.soup.find(itemprop="ratingValue")["content"])
        except TypeError:
            rating = None

        rank = self._string_grab("Rank")
        release_date = self.soup.time.string

        try:
            contact_url = self.url + [x.parent.a["href"] for x in self.misc if x.string == "Contact"][0]
        except IndexError:
            contact_url = None

        try:
            homepage = [x.parent.a["href"] for x in self.misc if x.string == "Homepage"][0]
        except IndexError:
            homepage = None

        try:
            last_update = [x.parent.time.string for x in self.misc if x.string == "Last Update"][0]
        except IndexError:
            last_update = None

        comment = self.url + "#commentform"

        articles = self._article_parser()
        tags = self._tag_parser(self.soup.find(id="tagsform").find_all(class_="row"))
        style = Style(*self._style_parser())
        suggestions = self._suggestion_parser()

        try:
            icon = [x.parent.img["src"] for x in self.misc if x.string == "Icon"][0]
        except IndexError:
            icon = None

        return desc, publishers, rating, rank, release_date, contact_url, homepage, last_update, comment, articles, tags, style, suggestions, icon

    def parse_game(self, moddb_url):        
        self.url = moddb_url
        self.soup, self.rss = self._soup_page()

        return Game(self.url, *self._general_parser(), *self._basic_game_parser(), self._share_parser())

    def parse_mod(self, moddb_url):
        self.url = moddb_url
        self.soup, self.rss = self._soup_page()

        return Mod(self.url, *self._general_parser(), *self._basic_mod_parser(), self._share_parser())

