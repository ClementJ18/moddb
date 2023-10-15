import pytest

import moddb

DEFAULT = "https://www.moddb.com/games/pokemon-generations/downloads/pokegen-v2-launcher"

pytestmark = [pytest.mark.vcr]


class TestFile:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        self.file = moddb.File(moddb.get_page(request.param))

    def test_get_comments(self):
        self.file.get_comments()
        self.file.get_comments(5)
