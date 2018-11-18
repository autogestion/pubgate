import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from pubgate.app import create_app
from tests.test_data import user_data


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