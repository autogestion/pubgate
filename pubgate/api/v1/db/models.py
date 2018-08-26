
from sanic_motor import BaseModel
# import flask_admin
# from flask_admin.contrib.pymongo.view import ModelView
from pubgate.api.v1.renders import ordered_collection


def actor_clean(data):
    return [item["activity"]["object"]["actor"] for item in data]


def activity_clean(data):
    return [item["activity"] for item in data]


async def get_ordered(request, model, filters, cleaner, coll_id):
    page = request.args.get("page")
    if page:
        total = None
        page = int(page)
    else:
        total = await model.count(filter=filters)
        page = 1

    limit = request.app.config.PAGINATION_LIMIT
    if total != 0:
        data = await model.find(filter=filters,
                                sort="activity.published desc",
                                skip=limit * (page - 1),
                                limit=limit)
        data = data.objects
    else:
        data = []
    resp = ordered_collection(coll_id, total, page, cleaner(data))
    return resp


class User(BaseModel):
    __coll__ = 'users'
    __unique_fields__ = ['username']

    async def followers_paged(self, request):
        filters = {
            "meta.deleted": False,
            "user_id": self.username,
            "activity.type": "Accept",
            "activity.object.type": "Follow"
        }
        coll_id = f"{request.app.v1_path}/user/{self.username}/followers"
        return await get_ordered(request, Outbox, filters, actor_clean, coll_id)

    async def following_paged(self, request):
        filters = {
            "meta.deleted": False,
            "users": {"$in": [self.username]},
            "activity.type": "Accept",
            "activity.object.type": "Follow"
        }
        coll_id = f"{request.app.v1_path}/user/{self.username}/following"
        return await get_ordered(request, Inbox, filters, actor_clean, coll_id)

    async def outbox_paged(self, request):
        filters = {
            "meta.deleted": False,
            "user_id": self.username
        }
        coll_id = f"{request.app.v1_path}/outbox/{self.username}"
        return await get_ordered(request, Outbox, filters, activity_clean, coll_id)

    async def inbox_paged(self, request):
        filters = {
            "meta.deleted": False,
            "users": {"$in": [self.username]}
        }
        coll_id = f"{request.app.v1_path}/inbox/{self.username}"
        return await get_ordered(request, Inbox, filters, activity_clean, coll_id)


class Outbox(BaseModel):
    __coll__ = 'outbox'
    __unique_fields__ = ['_id']


class Inbox(BaseModel):
    __coll__ = 'inbox'
    __unique_fields__ = ['_id']


async def register_admin(app):
    # TODO patch flask admin
    # admin = flask_admin.Admin(app, name='Pubgate Admin', template_mode='bootstrap3')
    #
    # # Add views
    # admin.add_view(ModelView(User))
    # admin.add_view(ModelView(Outbox))
    # admin.add_view(ModelView(Inbox))
    pass
