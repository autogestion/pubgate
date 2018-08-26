
from sanic import response, Blueprint
from sanic_openapi import doc

from pubgate.api.v1.db.models import User, Outbox
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
    id_list = resource.split(":")
    user_id, domain = id_list[1].split("@")

    if len(id_list) == 3:
        domain += f":{id_list[2]}"

    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"zrada": "no such user"}, status=404)

    resp = {
        "subject": f"acct:{user_id}@{domain}",
        "aliases": [
            # "{method}://mastodon.social/@user",
            f"{request.app.base_url}/api/v1/user/{user_id}"
        ],
        "links": [
            # {
            #     "rel": "http://webfinger.net/rel/profile-page",
            #     "type": "text/html",
            #     "href": "{method}://mastodon.social/@user"
            # },

            {
                "rel": "self",
                "type": "application/activity+json",
                "href": f"{request.app.base_url}/api/v1/user/{user_id}"
            },
            # {
            #     "rel": "salmon",
            #     "href": "{method}://mastodon.social/api/salmon/285169"
            # },

            # {
            #     "rel": "http://ostatus.org/schema/1.0/subscribe",
            #     "template": "{method}://mastodon.social/authorize_follow?acct={uri}"
            # }
        ]
    }
    return response.json(resp, headers={'Content-Type': 'application/activity+json; charset=utf-8'})


@well_known.route('/nodeinfo', methods=['GET'])
@doc.summary("nodeinfo")
async def nodeinfo(request):
    return response.json({"nodeName": request.app.config.DOMAIN})


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
