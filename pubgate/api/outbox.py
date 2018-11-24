
from sanic import response, Blueprint
from sanic_openapi import doc

from pubgate.db.models import Outbox
from pubgate.renders import context
from pubgate.activity import choose
from pubgate.utils.auth import user_check, token_check

outbox_v1 = Blueprint('outbox_v1')


@outbox_v1.route('/<user>/outbox', methods=['POST'])
@doc.summary("Post to user outbox, auth required")
@doc.consumes(Outbox, location="body")
@token_check
async def outbox_post(request, user):
    # TODO validate activity
    # TODO support mentions
    # TODO Accepts non-Activity Objects, and converts to Create Activities per 7.1.1
    # TODO merges audience properties (to, bto, cc, bcc, audience) with the Create's 'object's audience properties
    # TODO support collection

    activity = choose(user, request.json)
    await activity.save()
    await activity.deliver(debug=request.app.config.LOG_OUTGOING_REQUEST)

    return response.json({'peremoga': 'yep'},
                         status=201,
                         headers={'Location': activity.render["id"]}
                         )


@outbox_v1.route('/<user>/outbox', methods=['GET'])
@doc.summary("Returns user outbox")
@user_check
async def outbox_list(request, user):
    resp = await user.outbox_paged(request)
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})


@outbox_v1.route('/<user>/activity/<entity>', methods=['GET'])
@doc.summary("Returns activity from outbox")
@user_check
async def outbox_activity(request, user, entity):

    data = await Outbox.get(dict(user_id=user.name, _id=entity))
    if not data:
        return response.json({"zrada": "no such activity"}, status=404)

    result = data["activity"]
    result['@context'] = context

    return response.json(result, headers={'Content-Type': 'application/activity+json; charset=utf-8'})


@outbox_v1.route('/<user>/object/<entity>', methods=['GET'])
@doc.summary("Returns object from outbox")
@user_check
async def outbox_object(request, user, entity):

    data = await Outbox.get(dict(user_id=user.name, _id=entity))
    if not data:
        return response.json({"zrada": "no such object"}, status=404)

    result = data["activity"]["object"]
    result['@context'] = context

    return response.json(result, headers={'Content-Type': 'application/activity+json; charset=utf-8'})
