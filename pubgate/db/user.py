from sanic_motor import BaseModel
from simple_bcrypt import generate_password_hash
# import flask_admin
# from flask_admin.contrib.pymongo.view import ModelView
from pubgate.utils.user import UserUtils
from pubgate.db.boxes import Outbox, Inbox
from pubgate.db.managers import BaseManager


def actor_clean(data, striptags=False):
    return [item["activity"]["object"]["actor"] for item in data]


def actor_clean_inbox(data, striptags=False):
    return [item["activity"]["object"]["object"] for item in data]


def actor_clean_liked(data, striptags=False):
    return [item["activity"]["object"] for item in data]


class User(BaseModel, UserUtils, BaseManager):
    __coll__ = 'users'
    __unique_fields__ = ['name']


    # @classmethod
    # async def get(cls, name):
    #     user = await cls.find_one(dict(name=name))
    #     return user

    @classmethod
    async def create(cls, user_data, base_url):
        user_data["name"] = user_data.pop("username")
        user_data["password"] = generate_password_hash(user_data["password"])
        user_data["uri"] = f"{base_url}/@{user_data['name']}"
        await cls.insert_one(user_data)
        user = await cls.find_one({"name": user_data['name']})
        return user

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
        return await self.get_ordered(request, Outbox,
                                      self.followers_filter,
                                      actor_clean, self.followers)

    async def following_paged(self, request):
        return await self.get_ordered(request, Inbox,
                                      self.following_filter,
                                      actor_clean_inbox, self.following)

    async def liked_paged(self, request):
        filter = {
            "deleted": False,
            "user_id": self.name,
            "activity.type": "Like"
        }
        return await self.get_ordered(request, Outbox, filter,
                                      actor_clean_liked, self.liked)

    async def outbox_paged(self, request):
        filters = {
            "deleted": False,
            "user_id": self.name,
            "activity.type": "Create"
        }
        return await self.get_ordered(request, Outbox, filters,
                                      self.activity_clean, self.outbox)

    async def outbox_replies(self, request, entity):
        filters = {
            "deleted": False,
            "activity.type": "Create",
            "activity.object.inReplyTo": entity
        }
        return await self.get_replies(request, Outbox, Inbox, filters,
                                      self.activity_clean, f"{entity}/replies")

    async def inbox_paged(self, request):
        filters = {
            "deleted": False,
            "users": {"$in": [self.name]},
            "activity.type": "Create"
        }
        return await self.get_ordered(request, Inbox, filters,
                                      self.activity_clean, self.inbox)
