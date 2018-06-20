
from sanic import response, Blueprint
from sanic_openapi import doc

from pubgate.db.models import User

well_known = Blueprint('well_known', url_prefix='/.well-known')


# @well_known.middleware('response')
# async def update_headers(request, response):
#     response.headers["Content-Type"] = "application/jrd+json; charset=utf-8"


@well_known.route('/webfinger', methods=['GET'])
@doc.summary("webfinger")
async def webfinger(request):
    resource = request.args.get('resource')
    id = resource.split(":")[1].split("@")
    user_id, domain = id
    if not (domain == request.app.config.DOMAIN and await User.find_one(dict(username=user_id))):
        return response.json({"error": "no such user"}, status=404)

    resp = {
        "subject": "acct:autogestion@mastodon.social",
        "aliases": [
            # "https://mastodon.social/@user",
            f"https://{domain}/user/{user_id}"
        ],
        "links": [
            # {
            #     "rel": "http://webfinger.net/rel/profile-page",
            #     "type": "text/html",
            #     "href": "https://mastodon.social/@user"
            # },

            {
                "rel": "self",
                "type": "application/activity+json",
                "href": f"https://{domain}/user/{user_id}"
            },
            # {
            #     "rel": "salmon",
            #     "href": "https://mastodon.social/api/salmon/285169"
            # },

            # {
            #     "rel": "http://ostatus.org/schema/1.0/subscribe",
            #     "template": "https://mastodon.social/authorize_follow?acct={uri}"
            # }
        ]
    }
    return response.json(resp, headers={'Content-Type': 'application/jrd+json; charset=utf-8'})


@well_known.route('/nodeinfo', methods=['GET'])
@doc.summary("nodeinfo")
async def nodeinfo(request):
    return response.json({"nodeName": request.app.config.DOMAIN})
