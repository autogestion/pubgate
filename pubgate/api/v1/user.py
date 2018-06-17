
from sanic import response, Blueprint

user_v1 = Blueprint('user_v1', url_prefix='/api/v1/user')


@user_v1.route('/', methods=['POST'])
async def get_user(request):
    if request.app.config.OPEN_REGISTRATION:
        return response.json({'my': 'user_id'})
    return response.json({'my': 'nope'})


@user_v1.route('/<user_id', methods=['GET'])
async def get_user(request, user_id):
    return response.json({'my': user_id})