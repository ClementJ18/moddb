import time
import pyrate_limiter
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

@pytest.fixture(autouse=True, scope="module")
def client():
    return moddb.Client(username, password)

@pytest.fixture(autouse=True, scope="module")
def sender():
    return moddb.Client(sender_username, sender_password)


class TestClient:
    @pytest.mark.parametrize("watch_type", moddb.WatchType)
    def test_get_watched(self, watch_type, client: moddb.Client):
        client.get_watched(watch_type)

    def test_get_updates(self, client: moddb.Client):
        updates = client.get_updates()

        if updates:
            random.choice(updates).clear()

    @pytest.mark.parametrize("url", mixed_urls)
    def test_posts(self, url, client: moddb.Client):
        e = moddb.parse_page(url)
        client.tracking(e)  # follow
        client.tracking(e)  # unfollow

        if e.comments:
            comment = random.choice(e.comments.flatten())
            client.like_comment(comment)
            client.dislike_comment(comment)

        if isinstance(e, moddb.Group):
            client.membership(e)  # join
            client.membership(e)  # leave

    def test_friends(self, client: moddb.Client, sender: moddb.Client):
        sender.send_request(client.member)
        request = moddb.utils.get(
            client.get_friend_requests(), name=sender.member.profile.name
        )
        request.decline()

        sender.send_request(client.member)
        request = moddb.utils.get(
            client.get_friend_requests(), name=sender.member.profile.name
        )
        request.accept()

        client.unfriend(sender.member)

    def test_messages(self, client: moddb.Client, sender: moddb.Client):
        thread = sender.send_message([client.member], "Test", "This is a test message")
        thread = client.reply_to_thread(thread, "This is a test reply")

        member = moddb.parse_page("https://www.moddb.com/members/TheBetrayer")
        client.add_member_to_thread(thread, member)

        threads = client.get_threads()
        thumbnail = client.parse_thread(threads[0])

        client.leave_thread(thumbnail)
        client.mark_all_read()

    def test_add_comment(self, client: moddb.Client):
        page = moddb.parse_page("https://www.moddb.com/members/TheBetrayer")
        comment = client.add_comment(page, "Test Comment")

        with pytest.raises(pyrate_limiter.BucketFullException):
            client.add_comment(page, "Test Reply", comment=comment)

        time.sleep(60)

        client.add_comment(page, "Test Reply", comment=comment)

