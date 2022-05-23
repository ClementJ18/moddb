import unittest
import moddb

class TestJob(unittest.TestCase):
    def setUp(self):
        with open(getattr(self, "path", "test/fixtures/programmer-enviro-artist-audio-specialist-needed-to-expand-our-launched-game.html"), "r") as f:
            self.job = moddb.pages.Job(moddb.utils.soup(f.read()))

    def test_author_parse(self):
        self.job.author.parse()