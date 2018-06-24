import aiohttp
from sanic import Sanic
from sanic_openapi import swagger_blueprint, openapi_blueprint
from sanic_motor import BaseModel
# from little_boxes import set_debug
from little_boxes.activitypub import use_backend

from pubgate.db.backend import PGBackend
from pubgate.api.well_known import well_known
from pubgate.api.v1 import user_v1, inbox_v1, outbox_v1


def create_app(config_path):

    app = Sanic()
    app.config.from_pyfile(config_path)

    BaseModel.init_app(app)
    back = PGBackend()
    back.debug = app.config.DEBUG
    use_backend(back)
    app.config.back = back

    app.blueprint(openapi_blueprint)
    app.blueprint(swagger_blueprint)

    app.blueprint(well_known)
    app.blueprint(user_v1)
    app.blueprint(inbox_v1)
    app.blueprint(outbox_v1)

    app.add_task(register_aiohttp_pool(app))

    return app


async def register_aiohttp_pool(app):
    app.config.back.client_session = aiohttp.ClientSession()
