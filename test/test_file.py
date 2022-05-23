import unittest
import moddb

class TestFile(unittest.TestCase):
    def setUp(self):
        with open(getattr(self, "path", "test/fixtures/pokegen-v2-launcher.html"), "r") as f:
            self.file = moddb.pages.File(moddb.utils.soup(f.read()))

    def test_get_comments(self):
        self.file.get_comments()
        self.file.get_comments(5)
