import pytest
import random

from tests.test_utils import mixed_urls
from tests.test_config import username, password, sender_username, sender_password

import moddb

class TestClient:
    @pytest.fixture(autouse=True)
    def _get_object(self, _):
        self.client = moddb.Client(username, password)
        self.sender = moddb.Client(sender_username, sender_password)

    def test_get_watched(self):
        for e in moddb.WatchType:
            self.client.get_watched(e)

    def test_get_updates(self):
        updates = self.client.get_updates()

        if updates:
            random.choice(updates).clear()

    def test_posts(self):
        for url in mixed_urls:
            e = moddb.parse(url)
            self.client.tracking(e) #follow
            self.client.tracking(e) #unfollow

            if e.comments:
                comment = random.choice(e.comments.flatten())
                self.client.like_comment(comment)
                self.client.dislike_comment(comment)

            if isinstance(e, moddb.Group):
                self.client.membership(e) #join
                self.client.membership(e) #leave

    def test_friends(self):
        self.sender.send_request(self.client.member)
        request = moddb.utils.get(self.client.get_friend_requests(), name=self.sender.member.profile.name)
        request.decline()

        self.sender.send_request(self.client.member)
        request = moddb.utils.get(self.client.get_friend_requests(), name=self.sender.member.profile.name)
        request.accept()

        self.client.unfriend(self.sender.member)
