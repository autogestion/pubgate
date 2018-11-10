

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
