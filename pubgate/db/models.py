from sanic_motor import BaseModel
# import flask_admin
# from flask_admin.contrib.pymongo.view import ModelView
from pubgate.renders import ordered_collection
from pubgate.crypto.key import get_key


def actor_clean(data):
    return [item["activity"]["object"]["actor"] for item in data]


def actor_clean_inbox(data):
    return [item["activity"]["object"]["object"] for item in data]


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

    @property
    def key(self):
        return get_key(self.uri)

    @property
    def following(self): return f"{self.uri}/following"

    @property
    def followers(self): return f"{self.uri}/followers"

    @property
    def inbox(self): return f"{self.uri}/inbox"

    @property
    def outbox(self): return f"{self.uri}/outbox"

    async def followers_get(self):
        filters = {
            "meta.deleted": False,
            "user_id": self.name,
            "activity.type": "Accept",
            "activity.object.type": "Follow"
        }
        data = await Outbox.find(filter=filters)
        return list(set(actor_clean(data.objects)))

    async def followers_paged(self, request):
        filters = {
            "meta.deleted": False,
            "user_id": self.name,
            "activity.type": "Accept",
            "activity.object.type": "Follow"
        }
        return await get_ordered(request, Outbox, filters,
                                 actor_clean, self.followers)

    async def following_paged(self, request):
        filters = {
            "meta.deleted": False,
            "users": {"$in": [self.name]},
            "activity.type": "Accept",
            "activity.object.type": "Follow"
        }
        return await get_ordered(request, Inbox, filters,
                                 actor_clean_inbox, self.following)

    async def outbox_paged(self, request):
        filters = {
            "meta.deleted": False,
            "user_id": self.name
        }
        return await get_ordered(request, Outbox, filters,
                                 activity_clean, self.outbox)

    async def inbox_paged(self, request):
        filters = {
            "meta.deleted": False,
            "users": {"$in": [self.name]}
        }
        return await get_ordered(request, Inbox, filters,
                                 activity_clean, self.inbox)


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
