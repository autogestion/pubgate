from tests.test_data.well_known import nodeinfo, nodeinfo20, user_webfinger


class TestWellknown:
    async def test_webfinger(self, app, test_cli, user_data, user_webfinger):
        user_wf = await test_cli.get(f"/.well-known/webfinger?"
                                       f"resource=acct:{user_data['username']}@"
                                       f"{app.config.DOMAIN}")
        assert user_wf.status == 200
        wf = await user_wf.json()
        assert wf == user_webfinger

    async def test_nodeinfo(self, app, test_cli, nodeinfo):
        user_wf = await test_cli.get("/.well-known/nodeinfo")
        assert user_wf.status == 200
        wf = await user_wf.json()
        assert wf == nodeinfo

    async def test_nodeinfo20(self, app, test_cli, nodeinfo20):
        user_wf = await test_cli.get("/nodeinfo/2.0.json")
        assert user_wf.status == 200
        wf = await user_wf.json()
        assert wf == nodeinfo20
