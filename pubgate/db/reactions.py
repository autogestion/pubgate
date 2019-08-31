
from pubgate.db import Outbox, Inbox
from pubgate.renders import ordered_collection


class Reactions(Outbox):

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
    async def get_reactions(cls, request, filters, cleaner, coll_id):
        page = request.args.get("page")

        if page:
            total = None
            page = int(page)
        else:
            total1 = await Outbox.count(filter=filters)
            total2 = await Inbox.count(filter=filters)
            total = total1 + total2
            page = 1

        limit = request.app.config.PAGINATION_LIMIT
        if total != 0:
            data = await Outbox.aggregate(cls.aggregate_query + [
                {'$sort': {"activity.published": -1}},
                {'$match': filters},
                {'$limit': limit},
                {'$skip': limit * (page - 1)}
            ])
        else:
            data = []

        return ordered_collection(coll_id, total, page, cleaner(data))

    @classmethod
    async def likes(cls, request, entity):
        filters = {
            "deleted": False,
            "activity.type": "Like",
            "activity.object": entity
        }
        return await cls.get_reactions(request, filters,
                                       cls.activity_clean, f"{entity}/likes")

    @classmethod
    async def shares(cls, request, entity):
        filters = {
            "deleted": False,
            "activity.type": "Announce",
            "activity.object": entity
        }
        return await cls.get_reactions(request, filters,
                                       cls.activity_clean, f"{entity}/shares")

    @classmethod
    async def replies(cls, request, entity):
        filters = {
            "deleted": False,
            "activity.type": "Create",
            "activity.object.inReplyTo": entity
        }
        return await cls.get_reactions(request, filters,
                                       cls.activity_clean, f"{entity}/replies")