
import aiohttp
from sanic import response, Blueprint
from sanic_openapi import doc
from little_boxes.httpsig import verify_request
from little_boxes.activitypub import _to_list


from pubgate.api.v1.db.models import User, Inbox
from pubgate.api.v1.renders import ordered_collection

inbox_v1 = Blueprint('inbox_v1', url_prefix='/api/v1/inbox')


@inbox_v1.route('/<user_id>', methods=['POST'])
@doc.summary("Post to user inbox")
async def inbox_post(request, user_id):
    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)

    # profile = user_profile(request.app.config.back.base_url, user_id)
    activity = request.json.copy()

    # TODO verify signature
    # x = verify_request(
    #         request.method, request.path, request.headers, activity
    #     )
    #
    # print(x)

    # TODO skip blocked
    # if Outbox.find_one(
    #     {
    #         "activity.type": "Block",
    #         "user_id": user_id,
    #         "meta.undo": False,
    #     }):
    #     return response.json({"zrada": "actor is blocked"}, status=403)

    exists = await Inbox.find_one(dict(id=activity["id"]))
    if exists:

        if user_id in exists['users']:
            return response.json({"zrada": "activity allready exists"}, status=403)

        else:
            users = exists['users']
            users.append(user_id)
            await Inbox.update_one(
                {'_id': exists.id},
                {'$set': {"users": users}}
            )
    else:

        # TODO validate object, validate actor and activity
        # Disabled while issue  https://github.com/tsileo/little-boxes/issues/8 will be fixed
        # try:
        #     activity = await sync_to_async(parse_activity)(request.json)
        # except (UnexpectedActivityTypeError, BadActivityError) as e:
        #     return response.json({"zrada": e})

        await Inbox.insert_one({
                "id": activity["id"],
                "users": [user_id],
                # "actor_id": activity["acr"]
                "activity": activity,
                "type": activity["type"],
                "meta": {"undo": False, "deleted": False},
             })

    return response.json({'peremoga': 'yep'})


@inbox_v1.route('/<user_id>', methods=['GET'])
@doc.summary("Returns user inbox")
async def inbox_list(request, user_id):
    # TODO pagination

    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)

    data = await Inbox.find(filter={
        "meta.deleted": False,
        "users": {"$in": [user_id]}

    })

    inbox_url = f"{request.app.config.back.base_url}/inbox/{user_id}"
    cleaned = [item["activity"] for item in data.objects]
    resp = ordered_collection(inbox_url, cleaned)

    return response.json(resp, headers={'Content-Type': 'application/jrd+json; charset=utf-8'})