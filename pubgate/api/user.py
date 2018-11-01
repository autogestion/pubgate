
from simple_bcrypt import generate_password_hash
from sanic import response, Blueprint
from sanic_openapi import doc

from pubgate.renders import Actor
from pubgate.api.auth import user_check, token_check
from pubgate.db.models import User

user_v1 = Blueprint('user_v1')


@user_v1.route('/user', methods=['POST'])
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
            await User.insert_one(dict(name=username,
                                       password=generate_password_hash(password),
                                       email=request.json.get("email"),
                                       profile=request.json.get("profile"),
                                       details=request.json.get("details"),
                                       uri=f"{request.app.base_url}/{username}"
                                       )
                                  )
            return response.json({'peremoga': 'yep'}, status=201)
        else:
            return response.json({'zrada': 'username n/a'})


@user_v1.route('/<user>', methods=['PATCH'])
@doc.summary("Update user details or profile")
@token_check
async def user_get(request, user):

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

    return response.json({'peremoga': 'yep'}, status=201)


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
