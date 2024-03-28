import logging
import pytest

logger = logging.getLogger("vcr")
logger.setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def vcr_config():
    return {
        "filter_headers": ["User-Agent", "Cookie"],
        "filter_query_parameters": ["password", "username"],
        "filter_post_data_parameters": ["password", "username"],
    }
