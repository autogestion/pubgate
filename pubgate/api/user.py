from simple_bcrypt import check_password_hash
from sanic import response, Blueprint, exceptions
from sanic_openapi import doc

from pubgate.renders import Actor
from pubgate.utils import random_object_id
from pubgate.utils.checks import user_check, token_check, ui_app_check
from pubgate.db import User, Outbox
from pubgate.activity import Delete


user_v1 = Blueprint('user_v1')


@user_v1.route('/user', methods=['POST'])
@doc.summary("Creates a user")
@doc.consumes(User, location="body")
async def user_create(request):

    if request.app.config.REGISTRATION == "closed":
        return response.json({'error': 'registration closed'})

    invite = request.json.pop("invite", None)
    if request.app.config.REGISTRATION == "invite":
        if not invite or invite != request.app.config.INVITE_CODE:
            return response.json({'error': 'need valid invite'})

    username = request.json["username"].lower()
    password = request.json["password"]
    if username and password:
        is_uniq = await User.is_unique(doc=dict(name=username))
        if is_uniq in (True, None):
            user = await User.create(request.json, request.app.base_url)
            return response.json(
                {'profile': Actor(user).render(request.app.base_url)},
                status=201
            )
        else:
            return response.json({'error': 'username n/a'})


@user_v1.route('/@<user>', methods=['PATCH'])
@doc.summary("Update user details or profile")
@token_check
async def user_update(request, user):

    profile = request.json.get("profile")
    if profile:
        await User.update_one(
            {'name': user.name},
            {'$set': {"profile": profile}}
        )

    details = request.json.get("details")
    if details:
        for detail in details:
            await User.update_one(
                {'name': user.name},
                {'$set': {f"details.{detail}": details[detail]}}
            )

    return response.json({'Created': 'success'}, status=201)


@user_v1.route('/@<user>/mass_delete', methods=['POST'])
@doc.summary("Delete all user's posts")
@token_check
# TODO delete user's reactions (Like, Announce)
async def user_mass_delete(request, user):
    posts = await Outbox.find(filter={
        "deleted": False,
        "user_id": user.name,
        "activity.type": "Create"
    })
    for post in posts.objects:
        del_activity = Delete.construct(
            user, post.activity["object"]["id"]
        )
        await del_activity.save()
        await del_activity.deliver()
    return response.json({'Created': 'success'}, status=201)


@user_v1.route('/@<user>', methods=['GET'])
@doc.summary("Returns user profile")
@user_check
@ui_app_check
async def user_get(request, user):
    return response.json(
        Actor(user).render(request.app.base_url), headers={
            'Content-Type': 'application/activity+json; charset=utf-8'
        }
    )


@user_v1.route('/token', methods=['POST'])
@doc.summary("Get token")
async def token_get(request):
    user = await User.find_one(dict(
        name=request.json["username"].lower().lstrip('@')
    ))
    if not user:
        raise exceptions.NotFound("User not found")

    if not check_password_hash(user.password, request.json["password"]):
        return response.json({"error": "password incorrect"}, status=401)

    token = getattr(user, "token")
    if not token:
        token = random_object_id()
        #TODO make token expire
        await User.update_one({'name': request.json["username"]},
                              {'$set': {'token': token}})

    return response.json({'access_token': token})


@user_v1.route('/@<user>/followers', methods=['GET'])
@doc.summary("Returns user followers")
@user_check
async def followers_get(request, user):
    resp = await user.followers_paged(request)
    return response.json(resp, headers={
        'Content-Type': 'application/activity+json; charset=utf-8'
    })


@user_v1.route('/@<user>/following', methods=['GET'])
@doc.summary("Returns user following")
@user_check
async def following_get(request, user):
    resp = await user.following_paged(request)
    return response.json(resp, headers={
        'Content-Type': 'application/activity+json; charset=utf-8'
    })


@user_v1.route('/@<user>/liked', methods=['GET'])
@doc.summary("Returns user likes")
@user_check
async def liked_get(request, user):
    resp = await user.liked_paged(request)
    return response.json(resp, headers={
        'Content-Type': 'application/activity+json; charset=utf-8'
    })
