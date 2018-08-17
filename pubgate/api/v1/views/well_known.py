
from sanic import response, Blueprint
from sanic_openapi import doc

from pubgate.api.v1.db.models import User

well_known = Blueprint('well_known', url_prefix='/.well-known')


# @well_known.middleware('response')
# async def update_headers(request, response):
#     response.headers["Content-Type"] = "application/jrd+json; charset=utf-8"


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
    return response.json(resp, headers={'Content-Type': 'application/jrd+json; charset=utf-8'})


@well_known.route('/nodeinfo', methods=['GET'])
@doc.summary("nodeinfo")
async def nodeinfo(request):
    return response.json({"nodeName": request.app.config.DOMAIN})
