import asyncio

from sanic import response, Blueprint
from sanic_openapi import doc

from pubgate.db import Outbox
from pubgate.renders import context
from pubgate.activity import choose
from pubgate.utils.checks import user_check, token_check, outbox_check

outbox_v1 = Blueprint('outbox_v1')

# disabled because it affects all app blueprints, still bugged
# @outbox_v1.middleware('response')
# async def update_headers(request, response):
#     response.headers["Content-Type"] = "application/activity+json; charset=utf-8"


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
    # TODO implement streaming
    # if activity.render["type"] == "Create":
    #     await request.app.streams.outbox.put(activity.render)

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
@outbox_check
async def outbox_activity(request, user, entity):
    result = entity["activity"]
    result['@context'] = context
    return response.json(result, headers={'Content-Type': 'application/activity+json; charset=utf-8'})


@outbox_v1.route('/<user>/object/<entity>', methods=['GET'])
@doc.summary("Returns object from outbox")
@user_check
@outbox_check
async def outbox_object(request, user, entity):
    result = entity["activity"]["object"]
    result['@context'] = context
    return response.json(result, headers={'Content-Type': 'application/activity+json; charset=utf-8'})


@outbox_v1.route('/<user>/object/<entity>/replies', methods=['GET'])
@doc.summary("Returns replies for object")
@user_check
@outbox_check
async def outbox_replies(request, user, entity):
    resp = await user.outbox_replies(request, entity["activity"]["object"]["id"])
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})


@outbox_v1.route('/<user>/object/<entity>/likes', methods=['GET'])
@doc.summary("Returns likes for object")
@user_check
@outbox_check
async def outbox_likes(request, user, entity):
    resp = await user.outbox_likes(request, entity["activity"]["object"]["id"])
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})


@outbox_v1.route('/<user>/object/<entity>/shares', methods=['GET'])
@doc.summary("Returns shares for object")
@user_check
@outbox_check
async def outbox_shares(request, user, entity):
    resp = await user.outbox_shares(request, entity["activity"]["object"]["id"])
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})


@outbox_v1.route('/timeline/local', methods=['GET'])
@doc.summary("Returns local timeline")
async def outbox_all(request):
    resp = await Outbox.timeline_paged(request, f"{request.app.base_url}/timeline/local")
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})


# @outbox_v1.websocket('/timeline/local/stream')
# async def outbox_stream(request, ws):
#     while True:
#         update = await request.app.streams.outbox.get()
#         if update:
#             print('Sending: ')
#             await ws.send(update)
#         await asyncio.sleep(1)
