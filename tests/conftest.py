import pytest
import copy
from motor.motor_asyncio import AsyncIOMotorClient

from pubgate.app import create_app
from pubgate.db.user import User
from tests.test_data import user_data, user_profile
from tests.test_data.client_activity import s2c_follow
from tests.fakeserver import FakeServer


@pytest.fixture()
async def fake_server(loop):
    fake_remote = FakeServer(loop=loop)
    port = await fake_remote.start()
    yield port
    await fake_remote.stop()


@pytest.yield_fixture
def app():
    app = create_app('config/test.cfg')
    # app.client_session = app_session
    yield app
    client = AsyncIOMotorClient(app.config.MOTOR_URI)
    db = client.get_database()
    client.drop_database(db)


@pytest.fixture
def test_cli(loop, app, test_client):
    tc = loop.run_until_complete(test_client(app))
    app.base_url = f"{app.base_url}:{tc.port}"
    return tc


@pytest.fixture
def test_cli_invite_reg(loop, app, test_cli):
    app.config.REGISTRATION = "invite"
    return test_cli


@pytest.fixture
def test_cli_close_reg(loop, app, test_cli):
    app.config.REGISTRATION = "closed"
    return test_cli


@pytest.fixture
async def user(app, user_data):
    user_data = copy.deepcopy(user_data)
    user = await User.create(user_data, app.base_url)
    return user

