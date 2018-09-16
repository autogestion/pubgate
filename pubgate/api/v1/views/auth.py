from functools import wraps

from sanic import response, Blueprint, exceptions
from sanic_openapi import doc
from simple_bcrypt import generate_password_hash, check_password_hash

from pubgate.api.v1.db.models import User
from pubgate.api.v1.utils import random_object_id


auth_v1 = Blueprint('auth_v1')


def auth_required(handler=None):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        user = await User.find_one(dict(username=kwargs["user_id"],
                                        token=request.token))
        if not user:
            raise exceptions.Unauthorized("Auth required.")

        return await handler(request, *args, **kwargs)
    return wrapper


@auth_v1.route('/', methods=['POST'])
@doc.summary("Creates a user")
@doc.consumes(User, location="body")
async def user_create(request):

    if request.app.config.REGISTRATION == "closed":
        return response.json({'zrada': 'registration closed'})

    invite = request.json.pop("invite", None)
    if request.app.config.REGISTRATION == "invite":
        if not invite or invite != request.app.config.INVITE_CODE:
            return response.json({'zrada': 'need valid invite'})

    username = request.json["username"]
    password = request.json["password"]
    if username and password:
        is_uniq = await User.is_unique(doc=dict(username=username))
        if is_uniq in (True, None):
            await User.insert_one(dict(username=username,
                                       password=generate_password_hash(password),
                                       email=request.json.get("email"),
                                       actor_type=request.json.get("actor_type", "Person"),
                                       details=request.json.get("details"),
                                       renders={"domain": request.app.config.DOMAIN,
                                                "v1_path": request.app.v1_path}
                                       )
                                  )
            return response.json({'peremoga': 'yep'}, status=201)
        else:
            return response.json({'zrada': 'username n/a'})


@auth_v1.route('/token', methods=['POST'])
@doc.summary("Get token")
async def token_get(request):

    user = await User.find_one(dict(username=request.json["username"]))
    if not user:
        return response.json({"zrada": "username incorrect"}, status=401)

    if not check_password_hash(user.password, request.json["password"]):
        return response.json({"zrada": "password incorrect"}, status=401)

    token = getattr(user, "token")
    if not token:
        token = random_object_id()
        #TODO make token expire
        await User.update_one({'username': request.json["username"]},
                              {'$set': {'token': token}})

    return response.json({'token': token})