from sanic import response, Blueprint

outbox_v1 = Blueprint('outbox_v1', url_prefix='/api/v1/outbox')
