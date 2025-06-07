import logging
import time
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
    test_client,
    utils,
)

import moddb

logger = logging.getLogger("moddb")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="moddb.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)


@pytest.fixture(scope="class")
def delay():
    time.sleep(60)


@pytest.mark.vcr
class TestMods(test_mod.TestMod):
    @pytest.fixture(params=utils.mod_urls, autouse=True)
    def _get_object(self, request):
        self.mod = moddb.Mod(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestGames(test_game.TestGame):
    @pytest.fixture(params=utils.game_urls, autouse=True)
    def _get_object(self, request):
        self.game = moddb.Game(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestEngines(test_engine.TestEngine):
    @pytest.fixture(params=utils.engine_urls, autouse=True)
    def _get_object(self, request):
        self.engine = moddb.Engine(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestFiles(test_file.TestFile):
    @pytest.fixture(params=utils.file_urls, autouse=True)
    def _get_object(self, request):
        self.file = moddb.File(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestAddons(test_addon.TestAddon):
    @pytest.fixture(params=utils.addon_urls, autouse=True)
    def _get_object(self, request):
        self.addon = moddb.Addon(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestMedias(test_media.TestMedia):
    @pytest.fixture(params=utils.media_urls, autouse=True)
    def _get_object(self, request):
        self.media = moddb.Media(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestArticles(test_article.TestArticle):
    @pytest.fixture(params=utils.article_urls, autouse=True)
    def _get_object(self, request):
        self.article = moddb.Article(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestGroups(test_group.TestGroup):
    @pytest.fixture(params=utils.group_urls, autouse=True)
    def _get_object(self, request):
        self.group = moddb.Group(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestTeams(test_team.TestTeam):
    @pytest.fixture(params=utils.team_urls, autouse=True)
    def _get_object(self, request):
        self.team = moddb.Team(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestJobs(test_job.TestJob):
    @pytest.fixture(params=utils.job_urls, autouse=True)
    def _get_object(self, request):
        self.job = moddb.Job(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestMembers(test_member.TestMember):
    @pytest.fixture(params=utils.member_urls, autouse=True)
    def _get_object(self, request):
        self.member = moddb.Member(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestPlatforms(test_platform.TestPlatform):
    @pytest.fixture(params=utils.platform_urls, autouse=True)
    def _get_object(self, request):
        self.platform = moddb.Platform(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestHardwares(test_hardware.TestHardware):
    @pytest.fixture(params=utils.hardware_urls, autouse=True)
    def _get_object(self, request):
        self.hardware = moddb.Hardware(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestSoftwares(test_software.TestSoftware):
    @pytest.fixture(params=utils.software_urls, autouse=True)
    def _get_object(self, request):
        self.software = moddb.Software(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestPolls(test_poll.TestPoll):
    @pytest.fixture(params=utils.poll_urls, autouse=True)
    def _get_object(self, request):
        self.poll = moddb.Poll(moddb.get_page(request.param))


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestSearches(test_base.TestSearch):
    @pytest.fixture(params=utils.queries, autouse=True)
    def _get_object(self, request):
        self.search = moddb.search(request.param[1], query=request.param[0])


@pytest.mark.usefixtures("delay")
class TestLogin(test_base.TestLogin):
    pass


@pytest.mark.vcr
@pytest.mark.usefixtures("delay")
class TestFrontPage(test_base.TestFrontPage):
    pass


@pytest.mark.usefixtures("delay")
class TestClient(test_client.TestClient):
    pass
