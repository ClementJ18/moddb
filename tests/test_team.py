import pytest

from tests.utils import sample_list

import moddb

DEFAULT = "https://www.moddb.com/company/edainmod-dev-team"

pytestmark = [pytest.mark.vcr]


class TestTeam:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        self.team = moddb.Team(moddb.get_page(request.param))

    def test_get_addons(self):
        addons = self.team.get_addons()
        self.team.get_addons(2)
        self.team.get_addons(licence=moddb.Licence.public_domain)
        for addon in sample_list(addons, 3):
            addon.parse()

    def test_get_articles(self):
        articles = self.team.get_articles()
        self.team.get_articles(4)
        self.team.get_articles(category=moddb.ArticleCategory.news)

        for article in sample_list(articles, 3):
            article.parse()

    def test_get_comments(self):
        self.team.get_comments()
        self.team.get_comments(4)

    def test_get_engines(self):
        engines = self.team.get_engines()
        self.team.get_engines(3)

        for engine in sample_list(engines, 3):
            engine.parse()

    def test_get_files(self):
        files = self.team.get_files()
        self.team.get_files(4)
        self.team.get_files(category=moddb.FileCategory.demo)

        for file in sample_list(files, 3):
            file.parse()

    def test_get_games(self):
        games = self.team.get_games()
        self.team.get_games(3)

        for game in sample_list(games, 3):
            game.parse()

    def test_get_hardware(self):
        hardwares = self.team.get_hardware()
        self.team.get_hardware(3)

        for hardware in sample_list(hardwares, 3):
            hardware.parse()

    def test_get_images(self):
        images = self.team.get_images()

        for image in sample_list(images, 3):
            image.parse()

    def test_get_mods(self):
        mods = self.team.get_mods()
        self.team.get_mods(3)

        for mod in sample_list(mods, 3):
            mod.parse()

    def test_get_software(self):
        softwares = self.team.get_software()
        self.team.get_software(3)

        for software in sample_list(softwares, 3):
            software.parse()

    def test_get_tutorials(self):
        tutorials = self.team.get_tutorials()
        self.team.get_tutorials(3)
        self.team.get_tutorials(difficulty=moddb.Difficulty.basic)

        for tutorial in sample_list(tutorials, 3):
            tutorial.parse()

    def test_get_videos(self):
        videos = self.team.get_videos()

        for video in sample_list(videos, 3):
            video.parse()

    def test_get_watchers(self):
        self.team.get_watchers()

    def test_get_tags(self):
        tags = self.team.get_tags()
        # if tags:
        #     random.choice(tags)._get_members()
