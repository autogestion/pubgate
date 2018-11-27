import pytest
import copy
from motor.motor_asyncio import AsyncIOMotorClient

from pubgate.app import create_app
from pubgate.db.user import User
from tests.test_data import user_data, user_profile, user_webfinger


@pytest.yield_fixture
def app():
    app = create_app('config/test.cfg')
    yield app
    client = AsyncIOMotorClient(app.config.MOTOR_URI)
    db = client.get_database()
    client.drop_database(db)


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))


@pytest.fixture
def test_cli_invite_reg(loop, app, test_client):
    app.config.REGISTRATION = "invite"
    return loop.run_until_complete(test_client(app))


@pytest.fixture
def test_cli_close_reg(loop, app, test_client):
    app.config.REGISTRATION = "closed"
    return loop.run_until_complete(test_client(app))


@pytest.fixture
async def user(app, user_data):
    user_data = copy.deepcopy(user_data)
    user = await User.create(user_data, app.base_url)
    return user

