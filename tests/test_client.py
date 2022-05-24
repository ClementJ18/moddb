import unittest
from tests.utils import patched_request
from unittest.mock import patch
import moddb
import random

from tests.test_config import username, password, sender_username, sender_password

@patch("moddb.utils.request", new=patched_request)
class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = moddb.Client(username, password)
        self.sender = moddb.Client(sender_username, sender_password)

    def test_get_watched(self):
        for _, value in moddb.WatchType.__members__:
            self.client.get_watched(value)

    def test_get_updates(self):
        updates = self.client.get_updates()
        random.choice(updates).clear()

    def test_posts(self):
        urls = [
            "https://www.moddb.com/mods/edain-mod",
            "https://www.moddb.com/mods/the-horse-lords-a-total-modification-for-bfme",
            "https://www.moddb.com/mods/third-age-total-war",
            "https://www.moddb.com/games/battle-for-middle-earth-ii-rise-of-the-witch-king",
            "https://www.moddb.com/games/battle-for-middle-earth-ii",
            "https://www.moddb.com/games/battle-for-middle-earth",
            "https://www.moddb.com/engines/sage-strategy-action-game-engine",
            "https://www.moddb.com/engines/source",
            "https://www.moddb.com/engines/cryengine-3",
            "https://www.moddb.com/groups/humour-satire-parody",
            "https://www.moddb.com/groups/star-wars-empire-at-war-forces-of-corruption-mods",
            "https://www.moddb.com/groups/warhammer-40k-fans-group",
            "https://www.moddb.com/members/na3703168",
            "https://www.moddb.com/members/barneypan",
            "https://www.moddb.com/members/officialnecro"
        ]

        for url in urls:
            e = moddb.parse(url)
            self.client.tracking(e) #follow
            self.client.tracking(e) #unfollow

            comment = random.choice(e.comments.flatten())
            self.client.like_comment(comment)
            self.client.dislike_comment(comment)

            if isinstance(e, moddb.Group):
                self.client.membership(e) #join
                self.client.membership(e) #leave

    def test_friends(self):
        self.sender.send_request(self.client.member)
        request = moddb.utils.get(self.client.get_friend_requests(), name=self.sender.member.username)
        request.decline()

        self.sender.send_request(self.client.member)
        request = moddb.utils.get(self.client.get_friend_requests(), name=self.sender.member.username)
        request.accept()

        self.client.unfriend(self.sender.member)
