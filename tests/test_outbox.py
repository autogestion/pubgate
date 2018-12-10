import ujson

from tests.test_data.client_activity import follow


class TestFollow:
    async def test_follow(self, test_cli_app, remote_test_cli_app, user, follow):
        res = await test_cli_app.post(f"/{user.name}/outbox", data=ujson.dumps(follow))
        assert res.status == 201

        f_res = await remote_test_cli_app.get(f"/{user.name}/followers")

        f_res = await test_cli_app.get(f"/{user.name}/following")
        following = await res.json()
        assert follow["object"] in following["first"]["orderedItems"]

        f_res = await remote_test_cli_app.get(f"/{user.name}/followers")


