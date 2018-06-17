
from sanic import response, Blueprint
from sanic_openapi import doc

well_known = Blueprint('well_known', url_prefix='/.well-known')


# @well_known.middleware('response')
# async def update_headers(request, response):
#     response.headers["Content-Type"] = "application/jrd+json; charset=utf-8"


@well_known.route('/webfinger', methods=['GET'])
@doc.summary("webfinger")
async def webfinger(request):
    resource = request.args.get('resource')
    id = resource.split(":")
    resp = id
    return response.json(resp, headers={'Content-Type': 'application/jrd+json; charset=utf-8'})


@well_known.route('/nodeinfo', methods=['GET'])
@doc.summary("nodeinfo")
async def nodeinfo(request):
    return response.json({"nodeName": request.app.config.DOMAIN})
