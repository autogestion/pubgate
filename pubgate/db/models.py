import asyncio

from sanic_motor import BaseModel
# import flask_admin
# from flask_admin.contrib.pymongo.view import ModelView
from pubgate.renders import ordered_collection
from pubgate.crypto.key import get_key
from pubgate.utils import make_label, random_object_id
from pubgate.networking import deliver


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
    __unique_fields__ = ['name']

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
            "deleted": False,
            "user_id": self.name,
            "activity.type": "Accept",
            "activity.object.type": "Follow"
        }
        data = await Outbox.find(filter=filters)
        return list(set(actor_clean(data.objects)))

    async def followers_paged(self, request):
        filters = {
            "deleted": False,
            "user_id": self.name,
            "activity.type": "Accept",
            "activity.object.type": "Follow"
        }
        return await get_ordered(request, Outbox, filters,
                                 actor_clean, self.followers)

    async def following_paged(self, request):
        filters = {
            "deleted": False,
            "users": {"$in": [self.name]},
            "activity.type": "Accept",
            "activity.object.type": "Follow"
        }
        return await get_ordered(request, Inbox, filters,
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

    async def forward_to_followers(self, activity):
        recipients = await self.followers_get()
        try:
            recipients.remove(activity["actor"])
        except ValueError:
            pass
        asyncio.ensure_future(deliver(self.key, activity, recipients))


class Outbox(BaseModel):
    __coll__ = 'outbox'
    __unique_fields__ = ['_id']

    @classmethod
    async def save(cls, user, activity, **kwargs):
        db_obj = {
            "_id": activity.id,
            "user_id": user.name,
            "activity": activity.render,
            "label": make_label(activity.render),
            "deleted": False,
        }
        db_obj.update(kwargs)
        await Outbox.insert_one(db_obj)

    @classmethod
    async def delete(cls, obj_id):
        await cls.update_one(
            # {'activity.object.id': obj_id},
            {"$or": [{"activity.object.id": obj_id},
                     {"activity.object": obj_id}]},
            {'$set': {"deleted": True}}
        )


class Inbox(BaseModel):
    __coll__ = 'inbox'
    __unique_fields__ = ['_id', 'activity.id']

    @classmethod
    async def save(cls, user, activity):
        exists = await cls.find_one(
            {"activity.id": activity["id"]}
        )
        if exists:
            if user.name in exists['users']:
                return False

            else:
                users = exists['users']
                users.append(user.name)
                await cls.update_one(
                    {'_id': exists.id},
                    {'$set': {"users": users}}
                )

        else:
            # TODO validate actor and activity
            await cls.insert_one({
                "_id": random_object_id(),
                "users": [user.name],
                "activity": activity,
                "label": make_label(activity),
                "deleted": False,
                "first_user": user.name
            })
        return True

    @classmethod
    async def delete(cls, obj_id):
        # if undo:
        #     exists = await cls.find_one({"activity.id": obj_id,
        #                                  "deleted": False})
        # else:
        #     exists = await cls.find_one({"activity.object.id": obj_id,
        #                                  "deleted": False})
        exists = await cls.find_one({"$or": [{"activity.object.id": obj_id},
                                             {"activity.id": obj_id}],
                                     "deleted": False})
        if exists:
            await cls.update_one(
                {'_id': str(exists.id)},
                {'$set': {"deleted": True}}
            )
            return True
        return False


async def register_admin(app):
    # TODO patch flask admin
    # admin = flask_admin.Admin(app, name='Pubgate Admin', template_mode='bootstrap3')
    #
    # # Add views
    # admin.add_view(ModelView(User))
    # admin.add_view(ModelView(Outbox))
    # admin.add_view(ModelView(Inbox))
    pass
