import pytest


@pytest.fixture
def follow():
    return {
        "type": "Follow",
        "object": "https://mastodon.social/users/pubgate",
}
