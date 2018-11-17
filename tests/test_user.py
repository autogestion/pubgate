import ujson

from pubgate.db.user import User


class TestSignup:
    async def test_valid_signup(self, test_cli):
        payload = {
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
        res = await test_cli.post("/user", data=ujson.dumps(payload))
        resData = await res.json()
        assert res.status == 201

        created = await User.find_one(dict(name=payload["username"]))
        assert created.email == payload["email"]




