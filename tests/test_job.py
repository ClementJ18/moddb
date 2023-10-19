import pytest

import moddb

DEFAULT = "https://www.moddb.com/jobs/programmer-enviro-artist-audio-specialist-needed-to-expand-our-launched-game"

pytestmark = [pytest.mark.vcr]


class TestJob:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        self.job = moddb.Job(moddb.get_page(request.param))

    def test_author_parse(self):
        if self.job.author is not None:
            self.job.author.parse()
