import unittest
from tests.utils import patched_request
from unittest.mock import patch
import moddb

@patch("moddb.utils.request", new=patched_request)
class TestMedia(unittest.TestCase):
    def setUp(self):
        self.media = moddb.pages.Media(moddb.get_page(getattr(self, "url", "https://www.moddb.com/mods/third-age-total-war/videos/rohan7")))

    def test_get_comments(self):
        self.media.get_comments()
        self.media.get_comments(4)
