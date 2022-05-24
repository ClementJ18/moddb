import unittest
from tests.utils import patched_request
from unittest.mock import patch
import moddb

@patch("moddb.utils.request", new=patched_request)
class TestPoll(unittest.TestCase):
    def setUp(self):
        self.poll = moddb.pages.Poll(moddb.get_page(getattr(self, "url", "https://www.moddb.com/polls/total-conversions-vs-cosmetic-mods")))

    def test_get_comments(self):
        self.poll.get_comments()
        self.poll.get_comments(4)
