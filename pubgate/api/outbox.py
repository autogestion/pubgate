import asyncio

from sanic import response, Blueprint
from sanic_openapi import doc

from pubgate.db.models import Outbox
from pubgate.renders import context
from pubgate.activity import choose
from pubgate.utils.networking import deliver
from pubgate.api.auth import user_check, token_check

outbox_v1 = Blueprint('outbox_v1')


@outbox_v1.route('/<user>/outbox', methods=['POST'])
@doc.summary("Post to user outbox, auth required")
@doc.consumes(Outbox, location="body")
@token_check
async def outbox_post(request, user):
    # TODO handle replies
    # TODO validate activity
    # TODO support mentions

    activity = choose(user, request.json)
    await activity.save()
    # for field in ["to", "cc", "bto", "bcc"]:
    #     if field in activity.render:
    #         recipients.extend(_to_list(activity.render[field]))
    recipients = await activity.recipients()

    # post_to_remote_inbox
    asyncio.ensure_future(deliver(user.key, activity.render, recipients))

    return response.json({'peremoga': 'yep'})


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

    data = await Outbox.find_one(dict(user_id=user.name, _id=entity))
    if not data:
        return response.json({"zrada": "no such activity"}, status=404)

    result = data["activity"]
    result['@context'] = context

    return response.json(result, headers={'Content-Type': 'application/activity+json; charset=utf-8'})


@outbox_v1.route('/<user>/object/<entity>', methods=['GET'])
@doc.summary("Returns object from outbox")
@user_check
async def outbox_object(request, user, entity):

    data = await Outbox.find_one(dict(user_id=user.name, _id=entity))
    if not data:
        return response.json({"zrada": "no such activity"}, status=404)

    result = data["activity"]["object"]
    result['@context'] = context

    return response.json(result, headers={'Content-Type': 'application/activity+json; charset=utf-8'})
