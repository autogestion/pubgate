import ujson

from pubgate.db.user import User


class TestSignup:
    async def test_valid_signup(self, test_cli, user_data):
        res = await test_cli.post("/user", data=ujson.dumps(user_data))
        assert res.status == 201

        created = await User.find_one(dict(name=user_data["username"]))
        assert created.email == user_data["email"]
        assert created.name == user_data["username"]
        assert created.password != user_data["password"]

    async def test_unique_name(self, test_cli, user_data):
        res = await test_cli.post("/user", data=ujson.dumps(user_data))
        assert res.status == 201

        res = await test_cli.post("/user", data=ujson.dumps(user_data))
        assert res.status == 200
        users = await User.find(filter=dict(name=user_data["username"]))
        assert len(users.objects) == 1




