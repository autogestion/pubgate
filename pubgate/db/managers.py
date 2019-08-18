from aiocache.backends.memory import SimpleMemoryCache
from aiocache.serializers import JsonSerializer

from pubgate.renders import ordered_collection


class BaseManager:

    cache = SimpleMemoryCache(serializer=JsonSerializer())

    @classmethod
    async def get_by_uri(cls, object_id):
        activity = await cls.find_one(
            {"activity.object.id": object_id,
             "deleted": False}
        )
        return activity

    @classmethod
    async def delete(cls, obj_id):
        result = await cls.update_one(
            {"$or": [{"activity.object.id": obj_id},
                     {"activity.id": obj_id}],
             "deleted": False},
            {'$set': {"deleted": True}}
        )
        await cls.cache.clear()
        return result.modified_count

    @staticmethod
    def activity_clean(data):
        return [item["activity"] for item in data]

    @staticmethod
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

        return ordered_collection(coll_id, total, page, cleaner(data))

    @classmethod
    async def timeline_paged(cls, request, uri):
        filters = {
            "deleted": False,
            "activity.type": {'$in': ["Create", "Announce", "Like"]}
        }

        if cls.__coll__ == 'inbox':
            filters.update(
                {"users.0": {"$ne": "cached"}, "users": {"$size": 1}}
            )

        return await cls.get_ordered(
            request, cls, filters, cls.activity_clean, uri
        )
