from sanic_motor import BaseModel
from simple_bcrypt import generate_password_hash
# import flask_admin
# from flask_admin.contrib.pymongo.view import ModelView
from pubgate.utils import random_object_id
from pubgate.utils.user import UserUtils
from pubgate.db.boxes import Outbox, Inbox
from pubgate.db.managers import BaseManager


def actor_clean(data):
    return [item["activity"]["object"]["actor"] for item in data]


def actor_clean_inbox(data):
    return [item["activity"]["object"]["object"] for item in data]


def actor_clean_liked(data):
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
        user_data["alias"] = f"{base_url}/{user_data['name']}"
        user_data["uri"] = f"{base_url}/@{user_data['name']}"
        await cls.insert_one(user_data)
        user = await cls.find_one({"name": user_data['name']})
        return user

    def follow_filter(self, model):
        return {
            "deleted": False,
            **model.by_user(self.name),
            "activity.type": "Accept",
            "activity.object.type": "Follow"
        }

    async def followers_get(self):
        data = await Outbox.find(filter=self.follow_filter(Outbox))
        return list(set(actor_clean(data.objects)))

    async def followers_paged(self, request):
        return await self.get_ordered(request, Outbox,
                                      self.follow_filter(Outbox),
                                      actor_clean, self.followers)

    async def following_paged(self, request):
        return await self.get_ordered(request, Inbox,
                                      self.follow_filter(Inbox),
                                      actor_clean_inbox, self.following)

    async def liked_paged(self, request):
        filters = {
            "deleted": False,
            **Outbox.by_user(self.name),
            "activity.type": "Like"
        }
        return await self.get_ordered(request, Outbox, filters,
                                      actor_clean_liked, self.liked)

    async def outbox_paged(self, request):
        filters = {
            "deleted": False,
            **Outbox.by_user(self.name),
            "activity.type": {'$in': ["Create", "Announce", "Like"]}
        }
        return await self.get_ordered(request, Outbox, filters,
                                      self.activity_clean, self.outbox)

    async def inbox_paged(self, request):
        filters = {
            "deleted": False,
            **Inbox.by_user(self.name),
            "activity.type": {'$in': ["Create", "Announce", "Like"]}
        }
        return await self.get_ordered(request, Inbox, filters,
                                      self.activity_clean, self.inbox)


async def setup_cached_user(app, loop):
    exists = await User.find_one(dict(name="cached"))
    if not exists:
        await User.create({
            'username': 'cached',
            'password': random_object_id()
        }, app.base_url)
