#!/usr/bin/python3.6
from mod import *
from bs4 import BeautifulSoup
import requests

def _url_checker(url):
    return url.startswith("http://www.moddb.com/mods/")

def _soup_page(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    resp = requests.get(url.replace("www","rss") + "/articles/feed/rss.xml")
    rss = BeautifulSoup(resp.text, "xml")

    return soup, rss

def _article_parser(rss):
    articles = list()
    article_list = rss.find_all("item")
    for article in article_list:
        title = article.title.string
        desc = article.find_all(type="plain")[1].string
        link = article.link.string
        date = article.pubDate.string[:-14]
        articles.append(Article(title, desc, link, date))
    
    return articles

def _tag_parser(raw_tags, url):
    tags = list()
    for tag in raw_tags:
        name = tag.a.string
        link = url + tag.a["href"]
        tags.append(Tag(name, url))

    return tags

def _page_parser(url, soup, rss):

    def _string_grab1(string):
        try:
            return [x.parent.a.string for x in misc if x.string == string][0]
        except IndexError:
            return None

    misc = soup.find_all("h5")
    game = [x.parent.a for x in misc if x.string == "Game"][0]
    game_name = game.string
    game_url = "http://www.moddb.com" + game["href"]

    mod_name = soup.title.string[:-9].replace("for" + game_name, "")
    mod_url = url
    try:
        desc = str(soup.find(itemprop="description")["content"])
    except KeyError:
        desc = str(soup.find(itemprop="description").string)
    
    articles = _article_parser(rss)
    tags = _tag_parser(soup.find(id="tagsform").find_all(class_="row"), url)

    try: 
        publishers = [x.parent.a.string for x in misc if x.string in ["Developer", "Creator"]][0]
    except IndexError:
        publishers = None

    try:
        rating = soup.find(itemprop="ratingValue")["content"]
    except TypeError:
        rating = None

    release_date = soup.time.string

    theme = _string_grab1("Theme")
    genre = _string_grab1("Genre")
    players = _string_grab1("Players")
    rank = _string_grab1("Rank")
    visits_total_num = _string_grab1("Visits")
    files_num = _string_grab1("Files")
    articles_num = _string_grab1("Articles")
    reviews_num = _string_grab1("Reviews")
    homepage = _string_grab1("Homepage")
    followers_num = _string_grab1("Watchers")

    try:
        last_update = [x.parent.time.string for x in misc if x.string == "Last Update"][0]
    except IndexError:
        last_update = None

    suggestions = list()
    suggestions_raw = soup.find(string="You may also like").parent.parent.parent.parent.find_all(class_="row clear")
    for x in suggestions_raw:
        link = x.find("a",class_="heading")
        image_url = link.parent.parent.find("img")["src"]
        suggestion = Suggestion(link.string, link["href"], image_url)
        suggestions.append(suggestion)

    try:
        follow_url = url + [x.parent.a["href"] for x in misc if x.string == "Mod watch"][0]
    except IndexError:
        follow_url = None

    comment = url + "#commentform"

    return Mod(mod_name, game_name, mod_url, game_url, desc, articles, tags, followers_num, publishers, rating, genre, theme, players, rank, visits_total_num, files_num, articles_num, reviews_num, last_update, suggestions, homepage, follow_url, comment, release_date)

def parse_mod(url):
    if _url_checker(url):
        soup, rss = _soup_page(url)
        mod = _page_parser(url, soup, rss)
        return mod
    
