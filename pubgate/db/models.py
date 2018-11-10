from sanic_motor import BaseModel
# import flask_admin
# from flask_admin.contrib.pymongo.view import ModelView
from pubgate.utils import make_label, random_object_id
from pubgate.db.managers import BaseManager


class Outbox(BaseModel, BaseManager):
    __coll__ = 'outbox'
    __unique_fields__ = ['_id']

    @classmethod
    async def save(cls, activity, **kwargs):
        db_obj = {
            "_id": activity.id,
            "user_id": activity.user.name,
            "activity": activity.render,
            "label": make_label(activity.render),
            "deleted": False,
        }
        db_obj.update(kwargs)
        await Outbox.insert_one(db_obj)

    @classmethod
    async def unfollow(cls, activity):
        filters = activity.user.following_filter
        filters["activity.object.object"] = \
            activity.render["object"]["object"]
        accept = await Inbox.find_one(filters)
        if accept:
            activity.render["object"] = accept.activity["object"]
            await Inbox.update_one(
                {'_id': str(accept.id)},
                {'$set': {"deleted": True}}
            )
            await cls.update_one(
                {'activity.id': accept.activity["object"]["id"]},
                {'$set': {"deleted": True}}
            )


class Inbox(BaseModel, BaseManager):
    __coll__ = 'inbox'
    __unique_fields__ = ['_id', 'activity.id']

    @classmethod
    async def get_by_object(cls, object_id):
        activity = await cls.find_one(
            {"activity.object.id": object_id}
        )
        return activity

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
            pg_id = random_object_id()
            # TODO how to get single object from inbox
            # activity = copy.deepcopy(activity)
            # activity["pg_id"] = pg_id
            await cls.insert_one({
                "_id": pg_id,
                "users": [user.name],
                "activity": activity,
                "label": make_label(activity),
                "deleted": False,
                "first_user": user.name
            })
        return True


async def register_admin(app):
    # TODO patch flask admin
    # admin = flask_admin.Admin(app, name='Pubgate Admin', template_mode='bootstrap3')
    #
    # # Add views
    # admin.add_view(ModelView(User))
    # admin.add_view(ModelView(Outbox))
    # admin.add_view(ModelView(Inbox))
    pass
