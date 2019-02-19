import unittest
import moddb

class TestFrontPage(unittest.TestCase):
    def setUp(self):
        self.fp = moddb.front_page()

    def get_articles(self):
        for article in self.fp.articles:
            article.parse()

    def get_games(self):
        for game in self.fp.games:
            game.parse()

    def get_files(self):
        for file in self.fp.files:
            file.parse()
