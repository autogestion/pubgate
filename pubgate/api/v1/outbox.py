from sanic import response, Blueprint
from sanic_openapi import doc
from little_boxes.activitypub import parse_activity, Outbox, Person
from little_boxes.errors import UnexpectedActivityTypeError, BadActivityError

from pubgate.db.models import User
from pubgate.api.v1.user import render_user_profile

outbox_v1 = Blueprint('outbox_v1', url_prefix='/api/v1/outbox')


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

    try:
        activity = parse_activity(request.json)
    except (UnexpectedActivityTypeError, BadActivityError) as e:
        return response.json({"zrada": e})

    outbox = Outbox(Person(**profile))
    outbox.post(activity)

    return response.json(status=201, headers={"Location": activity.id})

