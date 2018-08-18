from functools import wraps

from sanic import response, Blueprint, exceptions
from sanic_openapi import doc

from pubgate.api.v1.db.models import User
from pubgate.api.v1.utils import random_object_id

auth_v1 = Blueprint('auth_v1', url_prefix='/api/v1/auth')


@auth_v1.route('/', methods=['POST'])
@doc.summary("Creates a user")
@doc.consumes(User, location="body")
async def user_create(request):
    if request.app.config.OPEN_REGISTRATION:
        username = request.json["username"]
        # TODO store password as hash
        password = request.json["password"]
        if username and password:
            is_uniq = await User.is_unique(doc=dict(username=username))
            if is_uniq in (True, None):
                await User.insert_one(dict(username=username,
                                           password=password,
                                           email=request.json["email"]))
                return response.json({'peremoga': 'yep'}, status=201)
            else:
                return response.json({'zrada': 'username n/a'})
    return response.json({'zrada': 'nope'})


@auth_v1.route('/token', methods=['POST'])
@doc.summary("Get token")
async def token_get(request):

    user = await User.find_one(dict(username=request.json["username"],
                                    password=request.json["password"]))
    if not user:
        return response.json({"zrada": "user or password incorrect"}, status=404)

    token = getattr(user, "token")
    if not token:
        token = random_object_id()
        #TODO make token expire
        await User.update_one({'username': request.json["username"]},
                              {'$set': {'token': token}})

    return response.json({'token': token})