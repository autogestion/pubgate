import pytest
import copy
from motor.motor_asyncio import AsyncIOMotorClient

from pubgate.app import create_app
from pubgate.db.user import User
from tests.test_data import user_data, user_profile

from sanic import Sanic
from sanic_motor import BaseModel
from pubgate.api import user_v1, inbox_v1, outbox_v1, well_known
from pubgate.logging import PGErrorHandler


def create_test_app(db_name, port):

    app = Sanic(error_handler=PGErrorHandler(), name=db_name)
    app.config.from_pyfile('config/base_sample_conf.cfg')
    app.config.MOTOR_URI = f'mongodb://localhost:27017/{db_name}'
    app.config.DOMAIN = f"localhost:{port}"
    app.base_url = f"{app.config.METHOD}://{app.config.DOMAIN}"

    BaseModel.init_app(app)

    app.blueprint(well_known)
    app.blueprint(user_v1)
    app.blueprint(inbox_v1)
    app.blueprint(outbox_v1)

    @app.middleware('request')
    async def print_on_request(request):
        BaseModel.__dbkey__ = request.app.name

    return app


@pytest.yield_fixture
def app():
    app = create_test_app('test_pbgate', 8000)
    yield app
    client = AsyncIOMotorClient(app.config.MOTOR_URI)
    db = client.get_database()
    client.drop_database(db)


@pytest.yield_fixture
def remote_app():
    app = create_test_app('remote_test_pbgate', 8008)
    yield app
    client = AsyncIOMotorClient(app.config.MOTOR_URI)
    db = client.get_database()
    client.drop_database(db)


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))


@pytest.fixture
def remote_test_cli(loop, remote_app, test_client):
    return loop.run_until_complete(test_client(remote_app))


@pytest.fixture
def test_cli_app(app, test_cli):
    app.config.DOMAIN = f"{test_cli.host}:{test_cli.port}"
    app.base_url = f"{app.config.METHOD}://{app.config.DOMAIN}"
    return test_cli


@pytest.fixture
def remote_test_cli_app(remote_app, remote_test_cli):
    remote_app.config.DOMAIN = f"{remote_test_cli.host}:{remote_test_cli.port}"
    remote_app.base_url = f"{remote_app.config.METHOD}://{remote_app.config.DOMAIN}"
    return remote_test_cli


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
    print("user")
    print(app.base_url)
    user_data = copy.deepcopy(user_data)
    user = await User.create(user_data, app.base_url, db='test_pbgate')
    return user


@pytest.fixture
async def remote_user(remote_app, user_data):
    print("remote_user")
    print(remote_app.base_url)
    user_data = copy.deepcopy(user_data)
    user = await User.create(user_data, remote_app.base_url, db='remote_test_pbgate')
    return user

