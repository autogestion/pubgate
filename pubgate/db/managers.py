from aiocache.backends.memory import SimpleMemoryCache
from aiocache.serializers import JsonSerializer

from pubgate.renders import ordered_collection


class BaseManager:

    cache = SimpleMemoryCache(serializer=JsonSerializer())

    aggregate_query = [
        {"$lookup": {
            "from": "inbox",
            "pipeline": [],
            "as": "inbox"}},
        {"$group": {
            "_id": "null",
            "outbox": {
                "$push": {
                    "_id": "$_id",
                    "activity": "$activity",
                    "deleted": "$deleted"}},
            "inbox": {
                "$first": "$inbox"}
        }},
        {"$project": {
            "items": {
                "$setUnion": ["$outbox", "$inbox"]
            }
        }},
        {"$unwind": "$items"},
        {"$replaceRoot": {"newRoot": "$items"}},
    ]

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
    async def get_replies(cls, request, t1, t2, filters, cleaner, coll_id):
        page = request.args.get("page")

        if page:
            total = None
            page = int(page)
        else:
            total1 = await t1.count(filter=filters)
            total2 = await t2.count(filter=filters)
            total = total1 + total2
            page = 1

        limit = request.app.config.PAGINATION_LIMIT
        if total != 0:
            data = await t1.aggregate(cls.aggregate_query + [
                {'$sort': {"activity.published": -1}},
                {'$match': filters},
                {'$limit': limit},
                {'$skip': limit * (page - 1)}
            ])
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
