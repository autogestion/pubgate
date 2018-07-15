
from sanic import response, Blueprint
from sanic_openapi import doc

from pubgate.api.v1.db.models import User
from pubgate.api.v1.renders import user_profile

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
                return response.json({'peremoga': 'yep'}, status=201)
            else:
                return response.json({'zrada': 'username n/a'})
    return response.json({'zrada': 'nope'})


@user_v1.route('/<user_id>', methods=['GET'])
@doc.summary("Returns user details")
async def get_user(request, user_id):
    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)

    return response.json(user_profile(request.app.config.back.base_url, user_id),
                         headers={'Content-Type': 'application/jrd+json; charset=utf-8'})

