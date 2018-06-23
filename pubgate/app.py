
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
    use_backend(back)
    app.config.back = back
    # set_debug(app.config.DEBUG)

    app.blueprint(openapi_blueprint)
    app.blueprint(swagger_blueprint)

    app.blueprint(well_known)
    app.blueprint(user_v1)
    app.blueprint(inbox_v1)
    app.blueprint(outbox_v1)

    return app
