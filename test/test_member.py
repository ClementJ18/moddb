import unittest
import moddb

class TestMember(unittest.TestCase):
    def setUp(self):
        self.member = moddb.pages.Member(moddb.soup(getattr(self, "url", "https://www.moddb.com/members/mladen1996")))

    def test_get_addons(self):
        addons = self.member.get_addons()
        self.member.get_addons(2)
        self.member.get_addons(licence=moddb.Licence.public_domain)
        for addon in addons:
            addon.parse()

    def test_get_articles(self):
        articles = self.member.get_articles()
        self.member.get_articles(4)
        self.member.get_articles(category=moddb.ArticleCategory.news)

        for article in articles:
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

        for file in files:
            file.parse()

    def test_get_friends(self):
        friends = self.member.get_friends()
        self.member.get_friends(3)

        for friend in friends:
            friend.parse()

    def test_get_games(self):
        games = self.member.get_games()
        self.member.get_games(3)

        for game in games:
            game.parse()

    def test_get_groups(self):
        groups = self.member.get_groups()
        self.member.get_groups(3)

        for group in groups:
            group.parse()

    def test_get_images(self):
        images = self.member.get_images()

        for image in images[:10]:
            image.parse()

    def test_get_mods(self):
        mods = self.member.get_mods()
        self.member.get_mods(3)

        for mod in mods:
            mod.parse()

    def test_get_reviews(self):
        self.member.get_reviews()
        self.member.get_reviews(3)

    def test_get_tutorials(self):
        tutorials = self.member.get_tutorials()
        self.member.get_tutorials(3)
        self.member.get_tutorials(difficulty=moddb.Difficulty.basic)

        for tutorial in tutorials:
            tutorial.parse()

    def test_get_comments(self):
        self.member.get_comments()
        self.member.get_comments(4)

    def test_get_videos(self):
        videos = self.member.get_videos()

        for video in videos:
            video.parse()


