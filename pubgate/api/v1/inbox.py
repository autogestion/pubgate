from sanic import response, Blueprint

inbox_v1 = Blueprint('inbox_v1', url_prefix='/api/v1/inbox')