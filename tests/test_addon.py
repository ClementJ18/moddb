import unittest
import moddb

class TestAddon(unittest.TestCase):
    def setUp(self):
        with open(getattr(self, "path", "test/fixtures/superman-sa-beta-v10.html"), "r") as f:
            self.addon = moddb.pages.Addon(moddb.utils.soup(f.read()))

    def test_get_comments(self):
        self.addon.get_comments()
        self.addon.get_comments(5)
