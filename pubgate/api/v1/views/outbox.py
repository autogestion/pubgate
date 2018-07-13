from sanic import response, Blueprint
from sanic_openapi import doc
from little_boxes.activitypub import parse_activity, Outbox, Person
from little_boxes.errors import UnexpectedActivityTypeError, BadActivityError

from pubgate.api.v1.db.models import User
from pubgate.api.v1.views.user import render_user_profile

outbox_v1 = Blueprint('outbox_v1', url_prefix='/api/v1/outbox')
from asgiref.sync import sync_to_async

@outbox_v1.route('/<user_id>', methods=['POST'])
@doc.summary("Post a user outbox")
async def outbox_post(request, user_id):
    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)

    profile = render_user_profile(request.app.config.METHOD,
                                  request.app.config.DOMAIN,
                                  user_id)

    if request.json["actor"] != profile["id"]:
        return response.json({"zrada": "incorect id"})

    request.app.config.back.profile = profile

    # async with request.app.config.back.client_session.get(request.json["actor"]) as resp:
    #     resp = await resp.json()

    try:
        # activity = parse_activity(request.json)
        activity = await sync_to_async(parse_activity)(request.json)
    except (UnexpectedActivityTypeError, BadActivityError) as e:
        return response.json({"zrada": e})

    outbox = Outbox(Person(**profile))
    # outbox.post(activity)
    await sync_to_async(outbox.post)(activity)

    return response.json({'peremoga': 'yep'}, status=201, headers={"Location": activity.id})


@outbox_v1.route('/<user_id>', methods=['GET'])
@doc.summary("Returns user outbox")
async def get_outbox(request, user_id):

    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)

    q = {
        # "box": Box.OUTBOX.value,
        "meta.deleted": False,
        "user_id": user_id
    }
    resp = await request.app.config.back.build_ordered_collection(
            # DB.activities,
            q=q,
            # cursor=request.args.get("cursor"),
            # map_func=lambda doc: activity_from_doc(doc, embed=True),
        )

    return response.json(resp, headers={'Content-Type': 'application/jrd+json; charset=utf-8'})