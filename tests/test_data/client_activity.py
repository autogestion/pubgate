import pytest


def s2c_follow(remote_user):
    return {
        "type": "Follow",
        "object": remote_user,
}
