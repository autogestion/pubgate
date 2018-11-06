import asyncio
from sanic import response, Blueprint
from sanic.log import logger
from sanic_openapi import doc

from pubgate.db.models import Inbox, Outbox
from pubgate.utils import check_original
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

    if activity["type"] == "Follow":
        saved = await Inbox.save(user, activity)
        if saved:
            deliverance = {
                "type": "Accept",
                "object": activity
            }
            deliverance = Activity(user, deliverance)
            await deliverance.save()
            # post_to_remote_inbox
            asyncio.ensure_future(deliver(user.key, deliverance.render, [activity["actor"]]))

    elif activity["type"] in ["Announce", "Like", "Create"]:
        # TODO validate if local object of reaction exists in outbox
        saved = await Inbox.save(user, activity)
        local = check_original(activity["object"], user.uri)
        if local and saved:
            await user.forward_to_followers(activity)

    elif activity["type"] == "Undo":
        deleted = await Inbox.delete(activity["object"]["id"])
        undo_obj = activity["object"].get("object", "")

        if undo_obj.startswith(user.uri) and deleted:
            if activity["object"]["type"] == "Follow":
                await Outbox.delete(activity["object"]["id"])
            elif activity["object"]["type"] in ["Announce", "Like"]:
                await user.forward_to_followers(activity)

    elif activity["type"] == "Delete":
        await Inbox.delete(activity["object"]["id"])
        # TODO handle(forward) delete of reply to local user post

    return response.json({'peremoga': 'yep'}, status=202)


@inbox_v1.route('/<user>/inbox', methods=['GET'])
@doc.summary("Returns user inbox, auth required")
@token_check
async def inbox_list(request, user):
    resp = await user.inbox_paged(request)
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})