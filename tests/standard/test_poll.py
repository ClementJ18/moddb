import pytest

import moddb

DEFAULT = "https://www.moddb.com/polls/total-conversions-vs-cosmetic-mods"

pytestmark = [pytest.mark.vcr]


class TestPoll:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        self.poll = moddb.Poll(moddb.get_page(request.param))

    def test_get_comments(self):
        self.poll.get_comments()
        self.poll.get_comments(4)
