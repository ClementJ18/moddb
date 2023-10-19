import pytest

import moddb

DEFAULT = "https://www.moddb.com/mods/third-age-total-war/videos/rohan7"

pytestmark = [pytest.mark.vcr]


class TestMedia:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        self.media = moddb.Media(moddb.get_page(request.param))

    def test_get_comments(self):
        self.media.get_comments()
        self.media.get_comments(4)
