import asyncio
from sanic import response, Blueprint
from sanic.log import logger
from sanic_openapi import doc

from pubgate.db import Inbox, Outbox
from pubgate.db.cached import timeline_cached
from pubgate.utils import check_origin
from pubgate.utils.networking import deliver, verify_request
from pubgate.utils.checks import user_check, token_check
from pubgate.utils.cached import ensure_cached
from pubgate.activity import Activity

inbox_v1 = Blueprint('inbox_v1')

@inbox_v1.middleware('response')
async def update_headers(request, response):
    response.headers["Access-Control-Allow-Origin"] = "*"


@inbox_v1.route('/<user>/inbox', methods=['POST'])
@doc.summary("Post to user inbox")
@doc.consumes(Inbox, location="body")
@user_check
async def inbox_post(request, user):
    # TODO implement shared inbox
    # TODO https://www.w3.org/TR/activitypub/#inbox-forwarding
    activity = request.json.copy()
    # TODO The receiver must verify the notification by fetching its source from the origin server.
    verified = await verify_request(request)
    if not verified:
        if getattr(request.app.config, 'DEBUG_INBOX', False):
            logger.info("signature incorrect")
        else:
            return response.json({"error": "signature incorrect"}, status=401)

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
            asyncio.ensure_future(deliver(user.key, deliverance.render, [activity["actor"]]))

    elif activity["type"] in ["Announce", "Like", "Create"]:
        # TODO validate if local object of reaction exists in outbox
        saved = await Inbox.save(user, activity)
        local_user = check_origin(activity["object"], user.uri)
        if saved:
            if local_user:
                await user.forward_to_followers(activity)
            elif activity["type"] in ["Announce", "Like"]:
                if not check_origin(activity["object"], request.app.base_url):
                    await ensure_cached(activity['object'])

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

    else:
        await Inbox.save(user, activity)

    return response.json({'peremoga': 'yep'}, status=202)


@inbox_v1.route('/<user>/inbox', methods=['GET'])
@doc.summary("Returns user inbox, auth required")
@token_check
async def inbox_list(request, user):
    resp = await user.inbox_paged(request)
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})


@inbox_v1.route('/timeline/federated', methods=['GET'])
@doc.summary("Returns federated timeline")
async def inbox_all(request):
    if request.args.get('cached'):
        resp = await timeline_cached(Inbox, request, f"{request.app.base_url}/timeline/federated")
    else:
        resp = await Inbox.timeline_paged(request, f"{request.app.base_url}/timeline/federated")
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})
