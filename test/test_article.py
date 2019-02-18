import unittest
import moddb

class TestArticle(unittest.TestCase):
    def setUp(self):
        self.article = moddb.pages.Article(moddb.soup(getattr(self, "url", "https://www.moddb.com/mods/third-age-total-war/videos/rohan7")))

    def test_get_comments(self):
        self.article.get_comments()
        self.article.get_comments(4)
