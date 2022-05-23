import unittest
import moddb

class TestMedia(unittest.TestCase):
    def setUp(self):
        with open(getattr(self, "path", "test/fixtures/rohan7.html"), "r") as f:
            self.media = moddb.pages.Media(moddb.utils.soup(f.read()))

    def test_get_comments(self):
        self.media.get_comments()
        self.media.get_comments(4)
