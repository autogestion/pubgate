
from sanic_motor import BaseModel
# import flask_admin
# from flask_admin.contrib.pymongo.view import ModelView


def follow_filter(user_id, actor=None):

    filter = {
        "meta.deleted": False,
        "activity.type": "Accept",
        "activity.object.type": "Follow"
    }
    if actor:
        filter.update({
            "activity.actor": actor,
            "users": {"$in": [user_id]}
        })
    else:
        filter.update({"user_id": user_id})

    return filter


class User(BaseModel):
    __coll__ = 'users'
    __unique_fields__ = ['username']

    async def get_followers(self, actor=None, paginate=None):
        # TODO support pagination
        data = await Outbox.find(filter=follow_filter(self.username))
        return [x["activity"]["object"]["actor"] for x in data.objects]

    async def check_following(self):
        return await Inbox.find_one(follow_filter(self.username))


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
