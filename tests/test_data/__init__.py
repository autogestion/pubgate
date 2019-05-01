import pytest


@pytest.fixture
def user_data():
    return {
            "username": "testuser",
            "password": "pass",
            "email": "bu",
            "profile": {
                "type": "Person",
                "name": "Test User",
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
        "preferredUsername": user_data['username'],
        "summary": user_data["profile"]["summary"],
        "icon": user_data["profile"]["icon"],
        "name": user_data["profile"]['name'],
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": f"{app.base_url}/{user_data['username']}",
        "following": f"{app.base_url}/{user_data['username']}/following",
        "followers": f"{app.base_url}/{user_data['username']}/followers",
        "inbox": f"{app.base_url}/{user_data['username']}/inbox",
        "outbox": f"{app.base_url}/{user_data['username']}/outbox",
        "liked": f"{app.base_url}/{user_data['username']}/liked",
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
