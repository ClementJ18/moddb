import pytest

import moddb

DEFAULT = "https://www.moddb.com/mods/brutal-doom/downloads/brutal-doom-v21-beta"

pytestmark = [pytest.mark.vcr]


class TestFile:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        self.file = moddb.File(moddb.get_page(request.param))

    def test_get_comments(self):
        self.file.get_comments()
        self.file.get_comments(5)
