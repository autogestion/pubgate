

def aggregate_boxes(push_fields=None):
    default = {
        "_id": "$_id",
        "activity": "$activity",
        "deleted": "$deleted"
    }
    if push_fields:
        default.update(push_fields)

    return [
        {"$lookup": {
            "from": "inbox",
            "pipeline": [],
            "as": "inbox"}},
        {"$group": {
            "_id": "null",
            "outbox": {
                "$push": push_fields},
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
        {'$sort': {"activity.published": -1}}
    ]
