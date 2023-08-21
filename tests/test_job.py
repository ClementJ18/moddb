import pytest
from unittest.mock import patch

from tests.utils import patched_request

import moddb

DEFAULT = "https://www.moddb.com/jobs/programmer-enviro-artist-audio-specialist-needed-to-expand-our-launched-game"


@patch("moddb.utils.request", new=patched_request)
class TestJob:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=patched_request) as f:
            self.job = moddb.Job(moddb.get_page(request.param))

    def test_author_parse(self):
        if self.job.author is not None:
            self.job.author.parse()
