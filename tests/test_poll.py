import pytest
from unittest.mock import patch

from tests.test_utils import patched_request

import moddb

DEFAULT = "https://www.moddb.com/polls/total-conversions-vs-cosmetic-mods"


@patch("moddb.utils.request", new=patched_request)
class TestPoll:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=patched_request) as f:
            self.poll = moddb.Poll(moddb.get_page(request.param))

    def test_get_comments(self):
        self.poll.get_comments()
        self.poll.get_comments(4)
