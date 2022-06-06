import logging
from unittest.mock import patch

from tests import test_utils

import moddb

logger = logging.getLogger("moddb")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="moddb.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


@patch("moddb.utils.request", new=test_utils.patched_request)
class TestParsers:
    mods = []
    games = []
    engines = []
    members = []

    def test_parse_mods(self):
        for url in test_utils.mod_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            self.mods.append(moddb.pages.Mod(soup))

    def test_parse_games(self):
        for url in test_utils.game_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            self.games.append(moddb.pages.Game(soup))

    def test_parse_engines(self):
        for url in test_utils.engine_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            self.engines.append(moddb.pages.Engine(soup))

    def test_parse_files(self):
        for url in test_utils.file_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            try:
                moddb.pages.File(soup)
            except ValueError as e:
                logger.debug(e)

    def test_parse_addons(self):
        for url in test_utils.addon_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            moddb.pages.Addon(soup)

    def test_parse_medias(self):
        for url in test_utils.media_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            moddb.pages.Media(soup)

    def test_parse_articles(self):
        for url in test_utils.article_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            moddb.pages.Article(soup)

    def test_parse_groups(self):
        for url in test_utils.group_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            moddb.pages.Group(soup)

    def test_parse_teams(self):
        for url in test_utils.team_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            moddb.pages.Team(soup)

    def test_parse_jobs(self):
        for url in test_utils.job_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            moddb.pages.Job(soup)

    def test_parse_members(self):
        for url in test_utils.member_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            self.members.append(moddb.pages.Member(soup))

    def test_parse_front_page(self):
        moddb.front_page()

    def test_parse_platforms(self):
        for url in test_utils.platform_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            moddb.pages.Platform(soup)

    def test_parse_hardware(self):
        for url in test_utils.hardware_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            moddb.pages.Hardware(soup)

    def test_parse_software(self):
        for url in test_utils.software_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            moddb.pages.Software(soup)

    def test_parse_polls(self):
        for url in test_utils.poll_urls:
            logger.debug(url)
            soup = moddb.get_page(url)
            moddb.pages.Poll(soup)

    def test_parse_reviews(self):
        for mod in self.mods:
            logger.debug(mod.url)
            mod.get_reviews()

        for game in self.games:
            logger.debug(game.url)
            game.get_reviews()

        for engine in self.engines:
            logger.debug(engine.url)
            engine.get_reviews()

    def test_parse_blogs(self):
        for member in self.members:
            logger.debug(member.url)
            member.get_blogs()
