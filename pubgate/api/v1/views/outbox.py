
from asgiref.sync import sync_to_async
from sanic import response, Blueprint
from sanic_openapi import doc

from little_boxes.activitypub import parse_activity, _to_list
from little_boxes.errors import UnexpectedActivityTypeError, BadActivityError

from pubgate.api.v1.db.models import User, Outbox
from pubgate.api.v1.renders import user_profile, ordered_collection, context

outbox_v1 = Blueprint('outbox_v1', url_prefix='/api/v1/outbox')


@outbox_v1.route('/<user_id>', methods=['POST'])
@doc.summary("Post to user outbox")
async def outbox_post(request, user_id):
    # TODO handle replies, post_to_remote_inbox
    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)

    profile = user_profile(request.app.config.back.base_url, user_id)
    activity = request.json.copy()

    if activity["actor"] != profile["id"]:
        return response.json({"zrada": "incorect id"})

    # Disabled while issue  https://github.com/tsileo/little-boxes/issues/8 will be fixed
    # try:
    #     activity = await sync_to_async(parse_activity)(request.json)
    # except (UnexpectedActivityTypeError, BadActivityError) as e:
    #     return response.json({"zrada": e})
    obj_id = request.app.config.back.random_object_id()

    await Outbox.insert_one({
            "_id": obj_id,
            "user_id": user_id,
            "activity": activity,
            "type": _to_list(activity["type"]),
            "meta": {"undo": False, "deleted": False},
         })

    return response.json({'peremoga': 'yep', 'id': obj_id})


@outbox_v1.route('/<user_id>', methods=['GET'])
@doc.summary("Returns user outbox")
async def outbox_list(request, user_id):
    # TODO pagination

    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)

    data = await Outbox.find(filter={
        "meta.deleted": False,
        "user_id": user_id
    })

    oubox_url = f"{request.app.config.back.base_url}/outbox/{user_id}"
    cleaned = []
    for item in data.objects:
        activity = item["activity"]
        activity["id"] = f"{oubox_url}/{item['_id']}"
        activity["object"]["id"] = f"{oubox_url}/{item['_id']}/activity"
        cleaned.append(activity)
    resp = ordered_collection(oubox_url, cleaned)

    return response.json(resp, headers={'Content-Type': 'application/jrd+json; charset=utf-8'})


@outbox_v1.route('/<user_id>/<activity_id>', methods=['GET'])
@doc.summary("Returns item from outbox")
async def outbox_item(request, user_id, activity_id):
    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)

    data = await Outbox.find_one(dict(user_id=user_id, _id=activity_id))
    if not data:
        return response.json({"zrada": "no such activity"}, status=404)

    outbox_url = f"{request.app.config.back.base_url}/outbox/{user_id}"
    activity = data["activity"]
    activity["id"] = f"{outbox_url}/{data['_id']}"
    activity["object"]["id"] = f"{outbox_url}/{data['_id']}/activity"
    activity['@context'] = context

    return response.json(activity, headers={'Content-Type': 'application/jrd+json; charset=utf-8'})


@outbox_v1.route('/<user_id>/<activity_id>/activity', methods=['GET'])
@doc.summary("Returns activity from outbox")
async def outbox_activity(request, user_id, activity_id):
    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)

    data = await Outbox.find_one(dict(user_id=user_id, _id=activity_id))
    if not data:
        return response.json({"zrada": "no such activity"}, status=404)

    outbox_url = f"{request.app.config.back.base_url}/outbox/{user_id}"
    activity = data["activity"]["object"]
    activity["id"] = f"{outbox_url}/{data['_id']}/activity"
    activity['@context'] = context

    return response.json(activity, headers={'Content-Type': 'application/jrd+json; charset=utf-8'})
