import unittest
import moddb

class TestArticle(unittest.TestCase):
    def setUp(self):
        with open(getattr(self, "path", "test/fixtures/rohan7.html"), "r") as f:
            self.article = moddb.pages.Article(moddb.utils.soup(f.read()))

    def test_get_comments(self):
        self.article.get_comments()
        self.article.get_comments(4)
