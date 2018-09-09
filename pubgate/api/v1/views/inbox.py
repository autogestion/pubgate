import asyncio
from sanic import response, Blueprint
from sanic.log import logger
from sanic_openapi import doc

from pubgate.api.v1.db.models import User, Inbox, Outbox
from pubgate.api.v1.utils import make_label, random_object_id
from pubgate.api.v1.networking import deliver, verify_request
from pubgate.api.v1.views.auth import auth_required

inbox_v1 = Blueprint('inbox_v1')


@inbox_v1.route('/<user_id>', methods=['POST'])
@doc.summary("Post to user inbox")
@doc.consumes(Inbox, location="body")
async def inbox_post(request, user_id):
    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)
    activity = request.json.copy()

    verified = await verify_request(
            request.method, request.path, request.headers, request.body
        )
    if not verified:
        if request.app.config.DEBUG:
            logger.info("signature incorrect")
        else:
            return response.json({"zrada": "signature incorrect"}, status=401)

    # TODO skip blocked
    # if Outbox.find_one(
    #     {
    #         "activity.type": "Block",
    #         "user_id": user_id,
    #         "meta.undo": False,
    #     }):
    #     return response.json({"zrada": "actor is blocked"}, status=403)

    exists = await Inbox.find_one(dict(_id=activity["id"]))
    if exists:
        if user_id in exists['users']:
            return response.json({"zrada": "activity already delivered"}, status=403)

        else:
            users = exists['users']
            users.append(user_id)
            await Inbox.update_one(
                {'_id': exists.id},
                {'$set': {"users": users}}
            )

    else:
        # TODO validate actor and activity
        await Inbox.insert_one({
                "_id": activity["id"],
                "users": [user_id],
                "activity": activity,
                "label": make_label(activity),
                "meta": {"undo": False, "deleted": False},
             })

    if activity["type"] == "Follow":
        obj_id = random_object_id()
        outbox_url = f"{request.app.v1_path}/outbox/{user_id}"
        deliverance = {
            "id": f"{outbox_url}/{obj_id}",
            "type": "Accept",
            "actor": activity["object"],
            "object": {
                "type": "Follow",
                "id": activity["id"],
                "actor": activity["actor"],
                "object": activity["object"]
            }
        }

        await Outbox.insert_one({
            "_id": obj_id,
            "user_id": user_id,
            "activity": deliverance,
            "label": make_label(deliverance),
            "meta": {"undo": False, "deleted": False},
        })

        # post_to_remote_inbox
        asyncio.ensure_future(deliver(deliverance, [activity["actor"]]))

    return response.json({'peremoga': 'yep'}, status=202)


@inbox_v1.route('/<user_id>', methods=['GET'])
@doc.summary("Returns user inbox, auth required")
@auth_required
async def inbox_list(request, user_id):
    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)

    resp = await user.inbox_paged(request)
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})