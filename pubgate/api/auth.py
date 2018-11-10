from functools import wraps

from sanic import response, Blueprint, exceptions
from sanic_openapi import doc
from simple_bcrypt import check_password_hash

from pubgate.db.user import User
from pubgate.utils import random_object_id


auth_v1 = Blueprint('auth_v1', url_prefix="auth")


def token_check(handler=None):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        user = await User.find_one(dict(name=kwargs["user"],
                                        token=request.token))
        if not user:
            raise exceptions.Unauthorized("Auth required.")

        kwargs["user"] = user
        return await handler(request, *args, **kwargs)
    return wrapper


def user_check(handler=None):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        user = await User.find_one(dict(name=kwargs["user"]))
        if not user:
            raise exceptions.Unauthorized("Incorrect username.")

        kwargs["user"] = user
        return await handler(request, *args, **kwargs)
    return wrapper


@auth_v1.route('/token', methods=['POST'])
@doc.summary("Get token")
async def token_get(request):

    user = await User.find_one(dict(name=request.json["username"]))
    if not user:
        return response.json({"zrada": "username incorrect"}, status=401)

    if not check_password_hash(user.password, request.json["password"]):
        return response.json({"zrada": "password incorrect"}, status=401)

    token = getattr(user, "token")
    if not token:
        token = random_object_id()
        #TODO make token expire
        await User.update_one({'name': request.json["username"]},
                              {'$set': {'token': token}})

    return response.json({'token': token})