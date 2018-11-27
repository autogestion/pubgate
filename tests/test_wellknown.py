

class TestWellknown:
    async def test_webfinger(self, app, test_cli, user_data, user_webfinger):
        user_wf = await test_cli.get(f"/.well-known/webfinger?"
                                       f"resource=acct:{user_data['username']}@"
                                       f"{app.config.DOMAIN}")
        assert user_wf.status == 200
        wf = await user_wf.json()
        assert wf == user_webfinger
