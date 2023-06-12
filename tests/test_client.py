import pytest
import random

from tests.utils import mixed_urls

try:
    from tests.test_config import username, password, sender_username, sender_password
except ModuleNotFoundError:
    import os

    username = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]
    sender_username = os.environ["SENDER_USERNAME"]
    sender_password = os.environ["SENDER_PASSWORD"]

import moddb


class TestClient:
    @pytest.fixture(autouse=True)
    def _get_object(self, request):
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
            e = moddb.parse_page(url)
            self.client.tracking(e)  # follow
            self.client.tracking(e)  # unfollow

            if e.comments:
                comment = random.choice(e.comments.flatten())
                self.client.like_comment(comment)
                self.client.dislike_comment(comment)

            if isinstance(e, moddb.Group):
                self.client.membership(e)  # join
                self.client.membership(e)  # leave

    def test_friends(self):
        self.sender.send_request(self.client.member)
        request = moddb.utils.get(self.client.get_friend_requests(), name=self.sender.member.profile.name)
        request.decline()

        self.sender.send_request(self.client.member)
        request = moddb.utils.get(self.client.get_friend_requests(), name=self.sender.member.profile.name)
        request.accept()

        self.client.unfriend(self.sender.member)

    def test_messages(self):
        thread = self.sender.send_message([self.client.member], "Test", "This is a test message")
        thread = self.client.reply_to_thread(thread, "This is a test reply")

        member = moddb.parse_page("https://www.moddb.com/members/TheBetrayer")
        self.client.add_member_to_thread(thread, member)

        threads = self.client.get_threads()
        thumbnail = self.client.parse_thread(threads[0])

        self.client.leave_thread(thumbnail)
        self.client.mark_all_read()
