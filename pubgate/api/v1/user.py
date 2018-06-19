
from sanic import response, Blueprint
from sanic_openapi import doc

from pubgate.db.models import User


user_v1 = Blueprint('user_v1', url_prefix='/api/v1/user')


@user_v1.route('/', methods=['POST'])
@doc.summary("Creates a user")
@doc.consumes(User, location="body")
async def create_user(request):
    if request.app.config.OPEN_REGISTRATION:
        username = request.json["username"]
        if username:
            is_uniq = await User.is_unique(doc=dict(username=username))
            if is_uniq in (True, None):
                await User.insert_one(dict(username=username,
                                           password=request.json["password"],
                                           email=request.json["email"]))
                return response.json({'peremoga': 'yep'})
            else:
                return response.json({'zrada': 'username n/a'})
    return response.json({'zrada': 'nope'})


@user_v1.route('/<user_id', methods=['GET'])
async def get_user(request, user_id):
    return response.json({'my': user_id})