import os

import aiohttp
from sanic import Sanic
from sanic_openapi import swagger_blueprint
from sanic_motor import BaseModel
from sanic_cors import CORS

from pubgate import MEDIA
from pubgate.api import user_v1, inbox_v1, outbox_v1, well_known
from pubgate.db import register_admin, setup_cached_user
from pubgate.logging import PGErrorHandler
from pubgate.utils.streams import Streams
from pubgate.utils.startapp import register_extensions, on_deploy_user


def create_app(config_path):

    app = Sanic(error_handler=PGErrorHandler())
    app.config.from_pyfile(config_path)

    app.config.DOMAIN = os.environ.get("DOMAIN", app.config.DOMAIN)
    app.base_url = f"{app.config.METHOD}://{app.config.DOMAIN}"
    # app.streams = Streams()
    db_host = os.environ.get("MONGODB_HOST", "localhost")
    app.config.MOTOR_URI = f'mongodb://{db_host}:27017/pbgate'
    BaseModel.init_app(app)
    CORS(app, automatic_options=True)

    # TODO Find viable openapi fork
    app.blueprint(swagger_blueprint)

    # app.blueprint(instance)
    app.blueprint(well_known)
    app.blueprint(user_v1)
    app.blueprint(inbox_v1)
    app.blueprint(outbox_v1)

    app.register_listener(
        setup_cached_user, 'before_server_start'
    )
    # app.add_task(register_client(app))
    # app.add_task(register_admin(app))
    register_extensions(app)

    app.static('/media', MEDIA)

    return app


async def register_client(app):
    app.client_session = aiohttp.ClientSession()







