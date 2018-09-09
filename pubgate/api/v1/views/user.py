
from sanic import response, Blueprint
from sanic_openapi import doc

from pubgate.api.v1.db.models import User
from pubgate.api.v1.renders import Actor


user_v1 = Blueprint('user_v1')


@user_v1.route('/<user_id>', methods=['GET'])
@doc.summary("Returns user details")
async def user_get(request, user_id):
    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)

    return response.json(Actor(request.app.v1_path, user_id, user.actor_type).render,
                         headers={'Content-Type': 'application/activity+json; charset=utf-8'})


@user_v1.route('/<user_id>/followers', methods=['GET'])
@doc.summary("Returns user followers")
async def followers_get(request, user_id):
    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)
    resp = await user.followers_paged(request)
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})


@user_v1.route('/<user_id>/following', methods=['GET'])
@doc.summary("Returns user following")
async def following_get(request, user_id):
    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)
    resp = await user.following_paged(request)
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})
