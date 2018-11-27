import pytest


@pytest.fixture
def user_data():
    return {
            "username": "testuser",
            "password": "pass",
            "email": "bu",
            "profile": {
                "type": "Person",
                "preferredUsername": "{{user}}",
                "summary": "activitypub federator, written on Python/ Sanic <a href='https://github.com/autogestion/pubgate' target='blank'> https://github.com/autogestion/pubgate</a>",
                "icon": {
                    "type": "Image",
                    "mediaType": "image/jpeg",
                    "url": "https://avatars2.githubusercontent.com/u/1098257"
                }
            }
        }


@pytest.fixture
def user_profile(app, user, user_data):
    return {
        "type": user_data["profile"]["type"],
        "preferredUsername": user_data["profile"]["preferredUsername"],
        "summary": user_data["profile"]["summary"],
        "icon": user_data["profile"]["icon"],
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {
                "Hashtag": "as:Hashtag",
                "sensitive": "as:sensitive"
            }
        ],
        "id": f"{app.base_url}/{user_data['username']}",
        "following": f"{app.base_url}/{user_data['username']}/following",
        "followers": f"{app.base_url}/{user_data['username']}/followers",
        "inbox": f"{app.base_url}/{user_data['username']}/inbox",
        "outbox": f"{app.base_url}/{user_data['username']}/outbox",
        "name": "",
        "manuallyApprovesFollowers": False,
        "publicKey": {
            "id": f"{app.base_url}/{user_data['username']}#main-key",
            "owner": f"{app.base_url}/{user_data['username']}",
            "publicKeyPem": f"{user.key.pubkey_pem}"
        },
        "endpoints": {
            "oauthTokenEndpoint": f"{app.base_url}/{user_data['username']}/token"
        }
    }


@pytest.fixture
def user_webfinger(app, user, user_data):
    return {
        "subject": f"acct:{user_data['username']}@{app.config.DOMAIN}",
        "aliases": [
            f"{app.base_url}/{user_data['username']}"
        ],
        "links": [
            {
                "rel": "self",
                "type": "application/activity+json",
                "href": f"{app.base_url}/{user_data['username']}"
            },
            {
                "rel": "magic-public-key",
                "href": user.key.to_magic_key()
            }
        ]
    }