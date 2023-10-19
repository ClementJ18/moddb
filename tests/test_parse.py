import logging

import pytest

from tests import utils

import moddb

logger = logging.getLogger("moddb")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="moddb.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

pytestmark = [pytest.mark.vcr]


class TestParsers:
    mods = []
    games = []
    engines = []
    members = []

    @pytest.mark.parametrize("url", utils.mod_urls)
    def test_parse_mods(self, url):
        soup = moddb.get_page(url)
        self.mods.append(moddb.pages.Mod(soup))

    @pytest.mark.parametrize("url", utils.game_urls)
    def test_parse_games(self, url):
        soup = moddb.get_page(url)
        self.games.append(moddb.pages.Game(soup))

    @pytest.mark.parametrize("url", utils.engine_urls)
    def test_parse_engines(self, url):
        soup = moddb.get_page(url)
        self.engines.append(moddb.pages.Engine(soup))

    @pytest.mark.parametrize("url", utils.file_urls)
    def test_parse_files(self, url):
        soup = moddb.get_page(url)
        try:
            moddb.pages.File(soup)
        except ValueError as e:
            logger.debug(e)

    @pytest.mark.parametrize("url", utils.addon_urls)
    def test_parse_addons(self, url):
        soup = moddb.get_page(url)
        moddb.pages.Addon(soup)

    @pytest.mark.parametrize("url", utils.media_urls)
    def test_parse_medias(self, url):
        soup = moddb.get_page(url)
        moddb.pages.Media(soup)

    @pytest.mark.parametrize("url", utils.article_urls)
    def test_parse_articles(self, url):
        soup = moddb.get_page(url)
        moddb.pages.Article(soup)

    @pytest.mark.parametrize("url", utils.group_urls)
    def test_parse_groups(self, url):
        soup = moddb.get_page(url)
        moddb.pages.Group(soup)

    @pytest.mark.parametrize("url", utils.team_urls)
    def test_parse_teams(self, url):
        soup = moddb.get_page(url)
        moddb.pages.Team(soup)

    @pytest.mark.parametrize("url", utils.job_urls)
    def test_parse_jobs(self, url):
        soup = moddb.get_page(url)
        moddb.pages.Job(soup)

    @pytest.mark.parametrize("url", utils.member_urls)
    def test_parse_members(self, url):
        soup = moddb.get_page(url)
        self.members.append(moddb.pages.Member(soup))

    def test_parse_front_page(self):
        moddb.front_page()

    @pytest.mark.parametrize("url", utils.platform_urls)
    def test_parse_platforms(self, url):
        soup = moddb.get_page(url)
        moddb.pages.Platform(soup)

    @pytest.mark.parametrize("url", utils.hardware_urls)
    def test_parse_hardware(self, url):
        soup = moddb.get_page(url)
        moddb.pages.Hardware(soup)

    @pytest.mark.parametrize("url", utils.software_urls)
    def test_parse_software(self, url):
        soup = moddb.get_page(url)
        moddb.pages.Software(soup)

    @pytest.mark.parametrize("url", utils.poll_urls)
    def test_parse_polls(self, url):
        soup = moddb.get_page(url)
        moddb.pages.Poll(soup)

    def test_parse_reviews(self):
        for mod in utils.sample_list(self.mods, 3):
            logger.debug(mod.url)
            mod.get_reviews()

        for game in utils.sample_list(self.games, 3):
            logger.debug(game.url)
            game.get_reviews()

        for engine in utils.sample_list(self.engines, 3):
            logger.debug(engine.url)
            engine.get_reviews()

    def test_parse_blogs(self):
        for member in utils.sample_list(self.members, 3):
            logger.debug(member.url)
            member.get_blogs()
