
from sanic import response, Blueprint
from sanic_openapi import doc

from pubgate.db.models import Outbox
from pubgate.db.user import User
from pubgate.renders import Actor
from pubgate import __version__


well_known = Blueprint('well_known')
instance = Blueprint('instance')

# @well_known.middleware('response')
# async def update_headers(request, response):
#     response.headers["Content-Type"] = "application/activity+json; charset=utf-8"


@well_known.route('/.well-known/webfinger', methods=['GET'])
@doc.summary("webfinger")
async def webfinger(request):
    resource = request.args.get('resource')
    if request.app.config.DOMAIN not in resource:
        return response.json({"error": "wrong domain"}, status=404)

    user_id = resource.split(":")[1].split("@")[0]
    user = await User.find_one(dict(name=user_id))
    if not user:
        return response.json({"error": "no such user"}, status=404)

    return response.json(Actor(user).webfinger(resource), headers={'Content-Type': 'application/jrd+json; charset=utf-8'})


@well_known.route('/nodeinfo/2.0.json', methods=['GET'])
@doc.summary("nodeinfo2.0")
async def nodeinfo20(request):
    users = await User.count()
    statuses = await Outbox.count(filter={
                                    "deleted": False,
                                    "activity.type": "Create"
                                })
    info = {
        "version": "2.0",
        "software": {
            "name": "PubGate",
            "version": __version__,
        },
        "protocols": ["activitypub"],
        "services": {"inbound": [], "outbound": []},
        "openRegistrations": request.app.config.REGISTRATION == "open",
        "usage": {"users": {"total": users}, "localPosts": statuses},
        "metadata": {
            "sourceCode": "https://github.com/autogestion/pubgate",
            # "nodeName": f"@{user.username}@{user.renders.domain}",
        },
    }

    return response.json(info,
                         headers={
                             "Content-Type": "application/json; profile="
                                             "http://nodeinfo.diaspora.software/ns/schema/2.0#"})


@well_known.route('/.well-known/nodeinfo', methods=['GET'])
@doc.summary("nodeinfo")
async def nodeinfo(request):
    return response.json({
        'links': [
             {
                 'rel': 'http://nodeinfo.diaspora.software/ns/schema/2.0',
                 'href': f'{request.app.base_url}/nodeinfo/2.0.json'
             }
        ]
    }, headers={'Content-Type': 'application/json; charset=utf-8'})
