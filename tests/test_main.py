from unittest.mock import patch
import logging
import pytest

from tests import (
    test_mod,
    test_game,
    test_engine,
    test_file,
    test_addon,
    test_media,
    test_article,
    test_group,
    test_team,
    test_job,
    test_member,
    test_platform,
    test_software,
    test_hardware,
    test_poll,
    test_base,

    test_utils,
    test_client,
)

import moddb

logger = logging.getLogger('moddb')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='moddb.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestMods(test_mod.TestMod):
    @pytest.fixture(params=test_utils.mod_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.mod = moddb.Mod(moddb.get_page(request.param))

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestGames(test_game.TestGame):
    @pytest.fixture(params=test_utils.game_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.game = moddb.Game(moddb.get_page(request.param))

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestEngines(test_engine.TestEngine):
    @pytest.fixture(params=test_utils.engine_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.engine = moddb.Engine(moddb.get_page(request.param))

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestFiles(test_file.TestFile):
    @pytest.fixture(params=test_utils.file_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.file = moddb.File(moddb.get_page(request.param))

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestAddons(test_addon.TestAddon):
    @pytest.fixture(params=test_utils.addon_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.addon = moddb.Addon(moddb.get_page(request.param))

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestMedias(test_media.TestMedia):
    @pytest.fixture(params=test_utils.media_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.media = moddb.Media(moddb.get_page(request.param))
    
@patch("moddb.utils.request", new=test_utils.patched_request)
class TestArticles(test_article.TestArticle):
    @pytest.fixture(params=test_utils.article_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.article = moddb.Article(moddb.get_page(request.param))

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestGroups(test_group.TestGroup):
    @pytest.fixture(params=test_utils.group_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.group = moddb.Group(moddb.get_page(request.param))

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestTeams(test_team.TestTeam):
    @pytest.fixture(params=test_utils.team_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.team = moddb.Team(moddb.get_page(request.param))

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestJobs(test_job.TestJob):
    @pytest.fixture(params=test_utils.job_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.job = moddb.Job(moddb.get_page(request.param))

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestMembers(test_member.TestMember):
    @pytest.fixture(params=test_utils.member_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.member = moddb.Member(moddb.get_page(request.param))

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestPlatforms(test_platform.TestPlatform):
    @pytest.fixture(params=test_utils.platform_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.platform = moddb.Platform(moddb.get_page(request.param))

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestHardwares(test_hardware.TestHardware):
    @pytest.fixture(params=test_utils.hardware_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.hardware = moddb.Hardware(moddb.get_page(request.param))

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestSoftwares(test_software.TestSoftware):
    @pytest.fixture(params=test_utils.software_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.software = moddb.Software(moddb.get_page(request.param))

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestPolls(test_poll.TestPoll):
    @pytest.fixture(params=test_utils.poll_urls, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.poll = moddb.Poll(moddb.get_page(request.param))

@patch("moddb.utils.request", new=test_utils.patched_request)
class TestSearches(test_base.TestSearch):
    @pytest.fixture(params=test_utils.queries, autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=test_utils.patched_request) as f:
            self.search= moddb.search(request.param[1], query=request.param[0])

class TestLogin(test_base.TestLogin):
    pass

class TestFrontPage(test_base.TestFrontPage):
    pass

class TestClient(test_client.TestClient):
    pass
