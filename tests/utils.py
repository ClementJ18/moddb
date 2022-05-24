import os
import logging
from unittest.mock import patch

import moddb

class FakeResponse:
    def __init__(self, text):
        self.text = text
        self.content = text.encode("utf-8")

request = moddb.utils.request
def patched_request(req):
    path = f"tests/fixtures{req.url.replace(moddb.BASE_URL, '')}.html"

    # cache the file if it doesn't exist
    if not os.path.exists(path):
        r = request(req)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(r.content)

    with open(path, "r") as f:
        return FakeResponse(f.read())
