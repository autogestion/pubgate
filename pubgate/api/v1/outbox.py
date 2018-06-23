from sanic import response, Blueprint
from sanic_openapi import doc
from little_boxes.activitypub import parse_activity, Outbox
from little_boxes.errors import UnexpectedActivityTypeError, BadActivityError

from pubgate.db.models import User

outbox_v1 = Blueprint('outbox_v1', url_prefix='/api/v1/outbox')


@outbox_v1.route('/<user_id>', methods=['POST'])
@doc.summary("Post a user outbox")
async def outbox_post(request, user_id):
    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)

    try:
        activity = parse_activity(request.json)
    except (UnexpectedActivityTypeError, BadActivityError) as e:
        return response.json({"zrada": e})

    Outbox.post(activity)

    return response.json(status=201, headers={"Location": activity.id})

