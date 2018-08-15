
from pubgate.api.v1.db.models import Outbox


async def get_followers(user_id, paginate=None):
    # TODO support pagination
    data = await Outbox.find(filter={
        "meta.deleted": False,
        "user_id": user_id,
        "activity.type": "Accept",
        "activity.object.type": "Follow"
    })
    return [x["activity"]["object"]["actor"] for x in data.objects]
