from datetime import datetime

from pubgate.utils import random_object_id, make_label
from pubgate.db.models import Outbox


class FollowersMixin:

    async def recipients(self):
        result = await self.user.followers_get()
        return list(set(result))


class Activity:

    def __init__(self, user, activity):
        self.id = random_object_id()
        self.render = activity
        self.user = user
        activity["id"] = f"{user.uri}/activity/{self.id}"

    async def save(self):
        await Outbox.insert_one({
            "_id": self.id,
            "user_id": self.user.name,
            "activity": self.render,
            "label": make_label(self.render),
            "meta": {"undo": False, "deleted": False},
        })


class Note(Activity, FollowersMixin):

    def __init__(self, user, activity):
        super().__init__(user, activity)
        published = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        activity["actor"] = user.uri
        activity["published"] = published

        activity["to"] = ["https://www.w3.org/ns/activitystreams#Public"]
        activity["cc"] = [user.followers]

        if isinstance(activity["object"], dict):
            activity["object"]["id"] = f"{user.uri}/object/{self.id}"
            activity["object"]["attributedTo"] = user.uri
            activity["object"]["published"] = published

            activity["object"]["to"] = ["https://www.w3.org/ns/activitystreams#Public"]
            activity["object"]["cc"] = [user.followers]


class Follow(Activity):

    def __init__(self, user, activity):
        super().__init__(user, activity)
        activity["actor"] = user.uri

    async def recipients(self):
        return self.render["object"]


class Delete(FollowersMixin):

    def __init__(self, user, activity):
        self.render = activity
        self.user = user
        activity["actor"] = user.uri
        activity["to"] = ["https://www.w3.org/ns/activitystreams#Public"]

    async def save(self):
        await Outbox.update_one(
            {'activity.object.id': self.render["object"]["id"]},
            {'$set': {"meta.deleted": True}}
        )


def choose(user, activity):
    atype = activity.get("type", None)
    otype = None
    aobj = activity.get("object", None)
    if aobj and isinstance(aobj, dict):
        otype = aobj.get("type", None)

    if atype == "Create":
        if otype == "Note":
            return Note(user, activity)

    elif atype == "Follow":
        return Follow(user, activity)

    elif atype == "Delete":
        return Delete(user, activity)

    return Activity(user, activity)
