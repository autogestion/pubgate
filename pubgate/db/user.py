from sanic_motor import BaseModel
# import flask_admin
# from flask_admin.contrib.pymongo.view import ModelView
from pubgate.renders import ordered_collection
from pubgate.utils.user import UserUtils
from pubgate.db.models import Outbox, Inbox


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


class User(BaseModel, UserUtils):
    __coll__ = 'users'
    __unique_fields__ = ['name']

    # @classmethod
    # async def get(cls, name):
    #     user = await cls.find_one(dict(name=name))
    #     return user

    @property
    def followers_filter(self):
        return {
            "deleted": False,
            "user_id": self.name,
            "activity.type": "Accept",
            "activity.object.type": "Follow"
        }

    @property
    def following_filter(self):
        return {
            "deleted": False,
            "users": {"$in": [self.name]},
            "activity.type": "Accept",
            "activity.object.type": "Follow"
        }

    async def followers_get(self):
        data = await Outbox.find(filter=self.followers_filter)
        return list(set(actor_clean(data.objects)))

    async def followers_paged(self, request):
        return await get_ordered(request, Outbox,
                                 self.followers_filter,
                                 actor_clean, self.followers)

    async def following_paged(self, request):
        return await get_ordered(request, Inbox,
                                 self.following_filter,
                                 actor_clean_inbox, self.following)

    async def outbox_paged(self, request):
        filters = {
            "deleted": False,
            "user_id": self.name
        }
        return await get_ordered(request, Outbox, filters,
                                 activity_clean, self.outbox)

    async def inbox_paged(self, request):
        filters = {
            "deleted": False,
            "users": {"$in": [self.name]}
        }
        return await get_ordered(request, Inbox, filters,
                                 activity_clean, self.inbox)
