import pytest


@pytest.fixture
def follow(remote_user):
    return {
        "type": "Follow",
        "object": remote_user.uri,
}
