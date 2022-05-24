import unittest
from tests.utils import patched_request
from unittest.mock import patch
import moddb

@patch("moddb.utils.request", new=patched_request)
class TestFile(unittest.TestCase):
    def setUp(self):
        self.file = moddb.pages.File(moddb.get_page(getattr(self, "url", "https://www.moddb.com/games/pokemon-generations/downloads/pokegen-v2-launcher")))

    def test_get_comments(self):
        self.file.get_comments()
        self.file.get_comments(5)
