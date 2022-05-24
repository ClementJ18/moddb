import unittest
from tests.utils import patched_request
from unittest.mock import patch
import moddb

@patch("moddb.utils.request", new=patched_request)
class TestArticle(unittest.TestCase):
    def setUp(self):
        self.article = moddb.pages.Article(moddb.get_page(getattr(self, "url", "https://www.moddb.com/mods/third-age-total-war/videos/rohan7")))

    def test_get_comments(self):
        self.article.get_comments()
        self.article.get_comments(4)
