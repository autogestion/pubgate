import aiohttp
from sanic import Sanic
from sanic_openapi import swagger_blueprint, openapi_blueprint
from sanic_motor import BaseModel

from pubgate.api.v1 import user_v1, inbox_v1, outbox_v1, well_known, auth_v1, instance
from pubgate.api.v1.db.models import register_admin


def create_app(config_path):

    app = Sanic()
    app.config.from_pyfile(config_path)
    app.base_url = f"{app.config.METHOD}://{app.config.DOMAIN}"
    BaseModel.init_app(app)

    # TODO Find viable openapi fork
    app.blueprint(openapi_blueprint)
    app.blueprint(swagger_blueprint)

    app.blueprint(auth_v1)
    app.blueprint(instance)
    app.blueprint(well_known)
    app.blueprint(user_v1)
    app.blueprint(inbox_v1)
    app.blueprint(outbox_v1)

    # app.add_task(register_client(app))
    app.add_task(register_admin(app))

    return app


async def register_client(app):
    app.client_session = aiohttp.ClientSession()
