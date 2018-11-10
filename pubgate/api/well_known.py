
from sanic import response, Blueprint
from sanic_openapi import doc

from pubgate.db.models import Outbox
from pubgate.db.user import User
from pubgate.renders import Actor
from pubgate import __version__, LOGO


well_known = Blueprint('well_known', url_prefix='/.well-known')
instance = Blueprint('instance')

# @well_known.middleware('response')
# async def update_headers(request, response):
#     response.headers["Content-Type"] = "application/activity+json; charset=utf-8"


@well_known.route('/webfinger', methods=['GET'])
@doc.summary("webfinger")
async def webfinger(request):
    resource = request.args.get('resource')
    if request.app.config.DOMAIN not in resource:
        return response.json({"zrada": "wrong domain"}, status=404)

    id_list = resource.split(":")[1].split("@")[0]
    user_id = id_list
    user = await User.find_one(dict(name=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)

    return response.json(Actor(user).webfinger(resource), headers={'Content-Type': 'application/jrd+json; charset=utf-8'})


@well_known.route('/nodeinfo', methods=['GET'])
@doc.summary("nodeinfo")
async def nodeinfo(request):
    users = await User.count()
    statuses = await Outbox.count(filter={
                                    "meta.deleted": False,
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
                "openRegistrations": False,
                "usage": {"users": {"total": users}, "localPosts": statuses},
                "metadata": {
                    "sourceCode": "https://github.com/autogestion/pubgate",
                    # "nodeName": f"@{user.username}@{user.renders.domain}",
                },
    }

    return response.json(info,
        headers={"Content-Type": "application/json; profile=http://nodeinfo.diaspora.software/ns/schema/2.0#"}
    )


@instance.route('/', methods=['GET'])
@doc.summary("Instance details")
async def instance_get(request):

    users = await User.count()
    statuses = await Outbox.count(filter={
                                    "meta.deleted": False,
                                    "activity.type": "Create"
                                })
    resp = {
        "uri": request.app.config.DOMAIN,
        "title": "PubGate",
        "description": "Asyncronous Lightweight ActivityPub Federator https://github.com/autogestion/pubgate",
        # "email": "hello@joinmastodon.org",
        "version": __version__,
        # "urls": {
        #     "streaming_api": "wss://mastodon.social"
        # },
        "stats": {
            "user_count": users,
            "status_count": statuses,
            # "domain_count": 5628
        },
        "thumbnail": LOGO,
        "languages": [
            "en"
        ]
    }

    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})
