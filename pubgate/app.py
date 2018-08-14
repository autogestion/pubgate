import aiohttp
from sanic import Sanic
from sanic_openapi import swagger_blueprint, openapi_blueprint
from sanic_motor import BaseModel
from little_boxes.activitypub import use_backend

from pubgate.api.v1.db.backend import PGBackend
from pubgate.api.v1 import user_v1, inbox_v1, outbox_v1, well_known
from pubgate.api.v1.db.models import register_admin


def create_app(config_path):

    app = Sanic()
    app.config.from_pyfile(config_path)

    BaseModel.init_app(app)
    back = PGBackend()
    back.debug = app.config.DEBUG
    back.base_url = f"{app.config.METHOD}://{app.config.DOMAIN}"
    use_backend(back)
    app.config.back = back

    register_admin
    app.blueprint(openapi_blueprint)
    app.blueprint(swagger_blueprint)

    app.blueprint(well_known)
    app.blueprint(user_v1)
    app.blueprint(inbox_v1)
    app.blueprint(outbox_v1)

    # app.add_task(register_client(app))
    app.add_task(register_admin(app))

    return app


async def register_client(app):
    app.config.back.client_session = aiohttp.ClientSession()
