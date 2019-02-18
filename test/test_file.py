import unittest
import moddb

class TestFile(unittest.TestCase):
    def setUp(self):
        self.file = moddb.pages.File(moddb.soup(getattr(self, "url", "https://www.moddb.com/games/pokemon-generations/downloads/pokegen-v2-launcher")))

    def test_get_comments(self):
        self.file.get_comments()
        self.file.get_comments(5)
