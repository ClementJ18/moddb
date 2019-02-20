import unittest
import moddb

class TestJob(unittest.TestCase):
    def setUp(self):
        self.job = moddb.pages.Job(moddb.soup(getattr(self, "url", "https://www.moddb.com/jobs/programmer-enviro-artist-audio-specialist-needed-to-expand-our-launched-game")))

    def test_author_parse(self):
        self.job.author.parse()