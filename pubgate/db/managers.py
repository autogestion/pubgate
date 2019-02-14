from pubgate.renders import ordered_collection
from pubgate.utils import strip_tags


class BaseManager:

    @classmethod
    async def delete(cls, obj_id):
        result = await cls.update_one(
            {"$or": [{"activity.object.id": obj_id},
                     {"activity.id": obj_id}],
             "deleted": False},
            {'$set': {"deleted": True}}
        )
        return result.modified_count

    @staticmethod
    def activity_clean(data, striptags=False):
        cleaned = [item["activity"] for item in data]
        if striptags:
            for post in cleaned:
                post["object"]["content"] = strip_tags(post["object"]["content"])
        return cleaned

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
        resp = ordered_collection(coll_id, total, page,
                                  cleaner(data, request.args.get("strip_tags")))
        return resp

    @staticmethod
    async def get_replies(request, t1, t2, filters, cleaner, coll_id):
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
            data = await t1.aggregate([
                {"$lookup": {
                    "from": "inbox",
                    "pipeline": [],
                    "as": "inbox"}},
                {"$group": {
                    "_id": "null",
                    "outbox": {
                        "$push": {
                            "_id":"$_id",
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
                {'$match': filters},
                {'$sort': {"activity.published": -1}},
                {'$limit': limit},
                {'$skip': limit * (page - 1)}
            ])
        else:
            data = []
        resp = ordered_collection(coll_id, total, page,
                                  cleaner(data, request.args.get("strip_tags")))
        return resp

    @classmethod
    async def timeline_paged(cls, request, uri):
        filters = {
            "deleted": False,
            "activity.type": "Create"
        }
        return await cls.get_ordered(request, cls, filters,
                                     cls.activity_clean, uri)
