import ujson
import logging
import aiohttp

from pubgate.db.boxes import Outbox
from tests.test_data.client_activity import s2c_follow
from tests.test_data.server_activity import s2s_follow

logger = logging.getLogger()


class TestFollow:
    async def test_follow(self, test_cli, user, fake_server):
        follow = s2c_follow(f"http://127.0.0.1:{fake_server}/user")

        res = await test_cli.post(f"/{user.name}/outbox", data=ujson.dumps(follow))
        assert res.status == 201

        db_follow = await Outbox.find_one({
            "deleted": False,
            "user_id": user.name,
            "activity.type": "Follow"
        })
        db_test_follow = s2s_follow(user.uri, follow["object"], db_follow["activity"]["id"])
        del db_test_follow['@context']
        assert db_test_follow == db_follow["activity"]

        #TODO replace this loop with comand which enforce executing of deliver tasks
        for x in range(5):
            async with aiohttp.ClientSession() as session:
                await session.get(follow["object"])

        following = await test_cli.get(f"/{user.name}/following")
        following_list = await following.json()
        assert follow["object"] in following_list["first"]["orderedItems"]
