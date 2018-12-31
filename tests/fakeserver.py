
import json
from aiohttp import web, ClientSession
from aiohttp.test_utils import unused_port


from tests.test_data.server_activity import s2s_follow

class FakeServer:
    def __init__(self, loop):
        self.loop = loop
        self.app = web.Application()
        self.runner = None
        self.port = None
        self.app.router.add_get('/user', self.user_profile)
        self.app.router.add_post('/user/inbox', self.inbox_post)

    async def start(self):
        self.port = port = unused_port()
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, '127.0.0.1', port)
        await site.start()
        return port

    async def stop(self):
        await self.runner.cleanup()

    async def inbox_post(self, request):
        data = await request.json()
        # from pprint import pprint
        # pprint(data)
        if data["type"] == "Follow":
            test_follow = s2s_follow(data["actor"], data["object"], data["id"])
            if not data == test_follow:
                raise
            accept = json.dumps({
                "type": "Accept",
                "id": "id",
                "object": data,
                "actor": data["object"]})
            async with ClientSession() as session:
                await session.post(f"{data['actor']}/inbox", data=accept)

        return web.json_response()

    async def user_profile(self, request):
        return web.json_response({
            "inbox": f"http://127.0.0.1:{self.port}/user/inbox"
        })


