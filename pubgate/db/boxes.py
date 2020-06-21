from datetime import datetime

from sanic_motor import BaseModel
from sanic.exceptions import SanicException

from pubgate.utils import make_label, random_object_id
from pubgate.db.managers import BaseManager
from pubgate.utils import check_origin


class Outbox(BaseModel, BaseManager):
    __coll__ = 'outbox'
    __unique_fields__ = ['_id']

    @staticmethod
    def by_user(name):
        return {"user_id": name}

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
    async def reaction_add(cls, activity, local, **kwargs):

        search_model = cls if local else Inbox
        add_to = await search_model.find_one(
            {"activity.object.id": activity.render['object']}
        )
        if add_to:
            if add_to.reactions and add_to.reactions.get(activity.render['type']):
                if add_to.reactions[activity.render['type']].get(activity.user.name):
                    raise SanicException(f'This post is already {activity.render["type"]}d', status_code=409)
            else:
                await cls.update_one(
                    {'_id': add_to.id},
                    {'$set': {f"reactions.{activity.render['type']}.{activity.user.name}":
                                  activity.render['id'],
                              "updated": datetime.now()}}
                )

        await cls.save(activity, **kwargs)

    @classmethod
    async def reaction_undo(cls, activity):
        reaction_type = activity.render['object']['type']
        local = check_origin(activity.render["object"]["object"], activity.render["actor"])
        search_model = cls if local else Inbox

        undo_from = await search_model.find_one(
            {"activity.object.id": activity.render['object']['object']}
        )
        if undo_from:
            if undo_from.reactions and undo_from.reactions.get(reaction_type) \
                    and undo_from.reactions[reaction_type].get(activity.user.name):
                await cls.update_one(
                    {'_id': undo_from.id},
                    {'$unset': {f"reactions.{reaction_type}.{activity.user.name}": 1}}
                )
            else:
                raise SanicException(f'This post is not {reaction_type}d', status_code=409)

        await cls.delete(activity.render["object"]["id"])

    @classmethod
    async def unfollow(cls, activity):
        filters = activity.user.follow_filter(Inbox)
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

    @staticmethod
    def by_user(name):
        return {"users": {"$in": [name]}}

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
                    {'$set': {"users": users,
                              "updated": datetime.now()}}
                )
                await cls.cache.clear()

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
                "first_user": user.name,
                "created": datetime.now()
            })
        # await cls.cache.clear()
        return True

    async def inbox_paged(self, request):
        filters = {
            "deleted": False,
            "activity.type": "Create"
        }
        return await self.get_ordered(request, Inbox, filters,
                                      self.activity_clean,
                                      f"{request.app.base_url}/timeline/federated")

    async def ensure_cached(cls, object_id):
        # TODO also fetch and cache reactions (replies, likes, shares)
        exists = await cls.get_by_uri(object_id)
        if not exists:
            cached_user = await User.find_one({'name': 'cached'})
            activity_object = await fetch(object_id)
            await cls.save(cached_user, {
                'type': 'Create',
                'id': f'{object_id}#activity',
                'published': activity_object['published'],
                'object': activity_object
            })


