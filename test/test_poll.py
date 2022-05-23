import unittest
import moddb

class TestPoll(unittest.TestCase):
    def setUp(self):
        with open(getattr(self, "path", "test/fixtures/total-conversions-vs-cosmetic-mods.html"), "r") as f:
            self.poll = moddb.pages.Poll(moddb.utils.soup(f.read()))

    def test_get_comments(self):
        self.poll.get_comments()
        self.poll.get_comments(4)
