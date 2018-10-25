
from sanic import response, Blueprint
from sanic_openapi import doc

from pubgate.renders import Actor
from pubgate.api.auth import user_check

user_v1 = Blueprint('user_v1')


@user_v1.route('/<user>', methods=['GET'])
@doc.summary("Returns user details")
@user_check
async def user_get(request, user):
    return response.json(Actor(user).render,
                         headers={'Content-Type': 'application/activity+json; charset=utf-8'})


@user_v1.route('/<user>/followers', methods=['GET'])
@doc.summary("Returns user followers")
@user_check
async def followers_get(request, user):
    resp = await user.followers_paged(request)
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})


@user_v1.route('/<user>/following', methods=['GET'])
@doc.summary("Returns user following")
@user_check
async def following_get(request, user):
    resp = await user.following_paged(request)
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})
