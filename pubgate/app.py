import aiohttp
from sanic import Sanic
from sanic_openapi import swagger_blueprint, openapi_blueprint
from sanic_motor import BaseModel

from pubgate.api.v1 import user_v1, inbox_v1, outbox_v1, well_known, auth_v1, instance
from pubgate.api.v1.db.models import register_admin
from pubgate.logging import PGErrorHandler


def create_app(config_path):

    app = Sanic(error_handler=PGErrorHandler())
    app.config.from_pyfile(config_path)
    app.base_url = f"{app.config.METHOD}://{app.config.DOMAIN}"
    app.v1_path = f"{app.base_url}{app.config.API_V1_PREFIX}"
    BaseModel.init_app(app)

    # TODO Find viable openapi fork
    app.blueprint(openapi_blueprint)
    app.blueprint(swagger_blueprint)

    auth_v1.url_prefix = f"{app.config.API_V1_PREFIX}/auth"
    instance.url_prefix = f"{app.config.API_V1_PREFIX}/instance"
    user_v1.url_prefix = f"{app.config.API_V1_PREFIX}/user"
    inbox_v1.url_prefix = f"{app.config.API_V1_PREFIX}/inbox"
    outbox_v1.url_prefix = f"{app.config.API_V1_PREFIX}/outbox"
    app.blueprint(auth_v1)
    # app.blueprint(instance)
    app.blueprint(well_known)
    app.blueprint(user_v1)
    app.blueprint(inbox_v1)
    app.blueprint(outbox_v1)

    app.add_task(register_client(app))
    app.add_task(register_admin(app))
    register_extensions(app)

    return app


async def register_client(app):
    app.client_session = aiohttp.ClientSession()


def register_extensions(app):
    extensions = app.config.EXTENSIONS
    for extension in extensions:
        ext = __import__(extension)

        ext_bps = getattr(ext, 'pg_blueprints')
        for bp in ext_bps:
            app.blueprint(bp)

        ext_tasks = getattr(ext, 'pg_tasks')
        for task in ext_tasks:
            task(app)
