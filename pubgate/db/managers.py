from pubgate.renders import ordered_collection


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
        resp = ordered_collection(coll_id, total, page, cleaner(data))
        return resp
