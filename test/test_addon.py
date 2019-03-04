import unittest
import moddb

class TestAddon(unittest.TestCase):
    def setUp(self):
        self.addon = moddb.pages.Addon(moddb.get_page(getattr(self, "url", "https://www.moddb.com/games/grand-theft-auto-san-andreas/addons/superman-sa-beta-v10")))

    def test_get_comments(self):
        self.addon.get_comments()
        self.addon.get_comments(5)
