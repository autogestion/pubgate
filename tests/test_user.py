import ujson

from pubgate.db.user import User


class TestSignup:
    async def test_valid_signup(self, app, test_cli, user_data):
        res = await test_cli.post("/user", data=ujson.dumps(user_data))
        assert res.status == 201

        created = await User.find_one(dict(name=user_data["username"]))
        assert created.email == user_data["email"]
        assert created.name == user_data["username"]
        assert created.password != user_data["password"]
        assert created.uri.startswith(app.base_url)

    async def test_unique_name(self, test_cli, user_data):
        res = await test_cli.post("/user", data=ujson.dumps(user_data))
        assert res.status == 201

        res = await test_cli.post("/user", data=ujson.dumps(user_data))
        assert res.status == 200
        users = await User.find(filter=dict(name=user_data["username"]))
        assert len(users.objects) == 1

    async def test_invite_registration(self, test_cli_invite_reg, user_data):
        res = await test_cli_invite_reg.post("/user", data=ujson.dumps(user_data))
        assert res.status == 200
        resp = await res.json()
        assert resp.get("error")

        user_data["invite"] = "invite"
        res = await test_cli_invite_reg.post("/user", data=ujson.dumps(user_data))
        assert res.status == 200
        resp = await res.json()
        assert resp.get("error")

        user_data["invite"] = "xyz"
        res = await test_cli_invite_reg.post("/user", data=ujson.dumps(user_data))
        assert res.status == 201

    async def test_closed_registration(self, test_cli_close_reg, user_data):
        res = await test_cli_close_reg.post("/user", data=ujson.dumps(user_data))
        assert res.status == 200
        resp = await res.json()
        assert resp.get("error")


class TestUser:
    pass