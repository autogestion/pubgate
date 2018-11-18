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