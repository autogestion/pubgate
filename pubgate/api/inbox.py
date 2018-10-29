import asyncio
from sanic import response, Blueprint
from sanic.log import logger
from sanic_openapi import doc

from pubgate.db.models import Inbox, Outbox
from pubgate.utils import make_label
from pubgate.networking import deliver, verify_request
from pubgate.api.auth import user_check, token_check
from pubgate.activity import Activity

inbox_v1 = Blueprint('inbox_v1')


@inbox_v1.route('/<user>/inbox', methods=['POST'])
@doc.summary("Post to user inbox")
@doc.consumes(Inbox, location="body")
@user_check
async def inbox_post(request, user):
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
        if user.name in exists['users']:
            return response.json({"zrada": "activity already delivered"}, status=403)

        else:
            users = exists['users']
            users.append(user.name)
            await Inbox.update_one(
                {'_id': exists.id},
                {'$set': {"users": users}}
            )

    else:
        # TODO validate actor and activity
        await Inbox.insert_one({
                "_id": activity["id"],
                "users": [user.name],
                "activity": activity,
                "label": make_label(activity),
                "meta": {"undo": False, "deleted": False},
             })

    if activity["type"] == "Follow":
        deliverance = {
            "type": "Accept",
            "actor": activity["object"],
            "object": {
                "type": "Follow",
                "id": activity["id"],
                "actor": activity["actor"],
                "object": activity["object"]
            }
        }
        deliverance = Activity(user, deliverance)

        await Outbox.insert_one({
            "_id": deliverance.id,
            "user_id": user.name,
            "activity": deliverance.render,
            "label": make_label(deliverance.render),
            "meta": {"undo": False, "deleted": False},
        })

        # post_to_remote_inbox
        asyncio.ensure_future(deliver(deliverance.render, [activity["actor"]]))

    elif (activity["type"] in ["Announce", "Like"] and
        activity["object"]["id"].startswith(user.uri)) or \
        (activity["type"] == "Create" and activity["object"]["inReplyTo"] and
        activity["object"]["inReplyTo"].startswith(user.uri)):
            recipients = await user.followers_get()
            recipients = list(set(recipients))
            try:
                recipients.remove(activity["actor"])
            except ValueError:
                pass
            asyncio.ensure_future(deliver(activity, recipients))

    return response.json({'peremoga': 'yep'}, status=202)


@inbox_v1.route('/<user>/inbox', methods=['GET'])
@doc.summary("Returns user inbox, auth required")
@token_check
async def inbox_list(request, user):
    resp = await user.inbox_paged(request)
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})