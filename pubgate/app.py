import aiohttp
from aiocache.backends.memory import SimpleMemoryCache
from aiocache.serializers import JsonSerializer
from sanic import Sanic
from sanic_openapi import swagger_blueprint, openapi_blueprint
from sanic_motor import BaseModel

from pubgate import MEDIA
from pubgate.api import user_v1, inbox_v1, outbox_v1, well_known
from pubgate.db import register_admin, setup_cached_user
from pubgate.logging import PGErrorHandler
from pubgate.utils.streams import Streams


def create_app(config_path):

    app = Sanic(error_handler=PGErrorHandler())
    app.config.from_pyfile(config_path)
    app.base_url = f"{app.config.METHOD}://{app.config.DOMAIN}"
    app.streams = Streams()
    app.cache = SimpleMemoryCache(serializer=JsonSerializer())
    BaseModel.init_app(app)

    # TODO Find viable openapi fork
    app.blueprint(openapi_blueprint)
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


def register_extensions(app):
    extensions = app.config.EXTENSIONS
    for extension in extensions:
        ext = __import__(extension)

        ext_bps = getattr(ext, 'pg_blueprints', [])
        for bp in ext_bps:
            app.blueprint(bp)

        ext_tasks = getattr(ext, 'pg_tasks', [])
        for task in ext_tasks:
            app.add_task(task)
