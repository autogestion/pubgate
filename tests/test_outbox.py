import ujson

from tests.test_data.client_activity import follow


class TestFollow:
    async def test_follow(self, app, test_cli, user):
        res = await test_cli.post(f"/{user.name}/outbox", data=ujson.dumps(follow))
        assert res.status == 201
