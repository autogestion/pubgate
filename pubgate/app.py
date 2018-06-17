
from sanic import Sanic
from sanic_openapi import swagger_blueprint, openapi_blueprint

from pubgate.api.well_known import well_known
from pubgate.api.v1 import user_v1, inbox_v1, outbox_v1


def create_app(config_path):

    app = Sanic()
    app.config.from_pyfile(config_path)

    app.blueprint(openapi_blueprint)
    app.blueprint(swagger_blueprint)

    app.blueprint(well_known)
    app.blueprint(user_v1)
    app.blueprint(inbox_v1)
    app.blueprint(outbox_v1)

    return app
