import pytest

from pubgate import __version__


@pytest.fixture
def user_webfinger(app, user, user_data):
    return {
        "subject": f"acct:{user_data['username']}@{app.config.DOMAIN}",
        "aliases": [
            f"{app.base_url}/@{user_data['username']}",
            f"{app.base_url}/{user_data['username']}"
        ],
        "links": [
            {
                "rel": "self",
                "type": "application/activity+json",
                "href": f"{app.base_url}/{user_data['username']}"
            },
            # {
            #     "rel": "magic-public-key",
            #     "href": user.key.to_magic_key()
            # }
        ]
    }


@pytest.fixture
def nodeinfo(app):
    return {
        "links": [
            {
                "rel": "http://nodeinfo.diaspora.software/ns/schema/2.0",
                "href": f"{app.base_url}/nodeinfo/2.0.json"
            }
        ]
    }


@pytest.fixture
def nodeinfo20():
    return {
        "version": "2.0",
        "software": {
            "name": "PubGate",
            "version": __version__
        },
        "protocols": [
            "activitypub"
        ],
        "services": {
            "inbound": [],
            "outbound": []
        },
        "openRegistrations": True,
        "usage": {
            "users": {
                "total": 0
            },
            "localPosts": 0
        },
        "metadata": {
            "sourceCode": "https://github.com/autogestion/pubgate"
        }
    }
