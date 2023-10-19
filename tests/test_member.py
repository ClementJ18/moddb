import pytest

from tests.utils import sample_list

import moddb
import requests

DEFAULT = "https://www.moddb.com/members/upstart"

pytestmark = [pytest.mark.vcr]


class TestMember:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        self.member = moddb.Member(moddb.get_page(request.param))

    def test_get_addons(self):
        addons = self.member.get_addons()
        self.member.get_addons(2)
        self.member.get_addons(licence=moddb.Licence.public_domain)
        for addon in sample_list(addons, 3):
            addon.parse()

    def test_get_articles(self):
        articles = self.member.get_articles()
        self.member.get_articles(4)
        self.member.get_articles(category=moddb.ArticleCategory.news)

        for article in sample_list(articles, 3):
            article.parse()

    def test_get_blogs(self):
        self.member.get_blogs()
        self.member.get_blogs(4)
        self.member.get_blogs(timeframe=moddb.TimeFrame.month)

    def test_get_comments(self):
        self.member.get_comments()
        self.member.get_comments(4)

    def test_get_files(self):
        files = self.member.get_files()
        self.member.get_files(4)
        self.member.get_files(category=moddb.FileCategory.demo)

        for file in sample_list(files, 3):
            file.parse()

    def test_get_friends(self):
        friends = self.member.get_friends()
        self.member.get_friends(3)

        for friend in sample_list(friends, 3):
            try:
                friend.parse()
            except requests.exceptions.HTTPError:
                pass

    def test_get_games(self):
        games = self.member.get_games()
        self.member.get_games(3)

        for game in sample_list(games, 3):
            game.parse()

    def test_get_groups(self):
        groups = self.member.get_groups()
        self.member.get_groups(3)

        for group in sample_list(groups, 3):
            group.parse()

    def test_get_images(self):
        images = self.member.get_images()

        for image in sample_list(images, 5):
            image.parse()

    def test_get_mods(self):
        mods = self.member.get_mods()
        self.member.get_mods(3)

        for mod in sample_list(mods, 3):
            mod.parse()

    def test_get_reviews(self):
        self.member.get_reviews()
        self.member.get_reviews(3)

    def test_get_tutorials(self):
        tutorials = self.member.get_tutorials()
        self.member.get_tutorials(3)
        self.member.get_tutorials(difficulty=moddb.Difficulty.basic)

        for tutorial in sample_list(tutorials, 3):
            tutorial.parse()

    def test_get_comments(self):
        self.member.get_comments()
        self.member.get_comments(4)

    def test_get_videos(self):
        videos = self.member.get_videos()

        for video in sample_list(videos, 3):
            video.parse()

    def test_get_watchers(self):
        self.member.get_watchers()

    def test_get_tags(self):
        tags = self.member.get_tags()
        # if tags:
        #     random.choice(tags)._get_members()
