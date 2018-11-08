from datetime import datetime

from pubgate.utils import random_object_id, reply_origin
from pubgate.db.models import Outbox, Inbox


class Activity:

    def __init__(self, user, activity):
        self.id = random_object_id()
        self.render = activity
        self.user = user
        self.cc = []
        activity["id"] = f"{user.uri}/activity/{self.id}"
        activity["actor"] = user.uri
    #
    # @staticmethod
    # async def get_target(obj_id):
    #     target = await Inbox.get_by_object(obj_id)
    #     if not target:
    #         target = await fetch(obj_id)
    #     return target["object"]["attributedTo"]

    @property
    def published(self):
        return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    async def save(self):
        await Outbox.save(self)

    async def recipients(self):
        result = await self.user.followers_get()
        result.extend(self.cc)
        return list(set(result))


class Follow(Activity):

    async def recipients(self):
        return [self.render["object"]]


class Create(Activity):

    def __init__(self, user, activity):
        super().__init__(user, activity)
        activity["published"] = activity["object"]["published"] = self.published

        activity["to"] = activity["object"]["to"] = \
            ["https://www.w3.org/ns/activitystreams#Public"]

        activity["object"]["id"] = f"{user.uri}/object/{self.id}"
        activity["object"]["attributedTo"] = user.uri


class Post(Create):
    def __init__(self, user, activity):
        super().__init__(user, activity)
        activity["cc"] = activity["object"]["cc"] = [user.followers]


class Reply(Create):
    def __init__(self, user, activity):
        super().__init__(user, activity)
        self.cc = activity["cc"][:]
        activity["cc"].insert(0, user.followers)
        activity["object"]["cc"].insert(0, user.followers)


class Reaction(Activity):

    def __init__(self, user, activity):
        super().__init__(user, activity)
        self.cc = activity["cc"][:]
        activity["cc"].insert(0, user.followers)
        activity["published"] = self.published
        activity["to"] = ["https://www.w3.org/ns/activitystreams#Public"]


class Delete:
    # TODO check if post have mentions to add to recipients

    def __init__(self, user, activity):
        self.render = activity
        self.user = user
        activity["actor"] = user.uri
        activity["to"] = ["https://www.w3.org/ns/activitystreams#Public"]

    async def save(self):
        await Outbox.delete(self.render["object"]["id"])


def choose(user, activity):
    atype = activity.get("type", None)
    otype = None
    aobj = activity.get("object", None)
    if aobj and isinstance(aobj, dict):
        otype = aobj.get("type", None)

    if atype == "Create":
        local = reply_origin(aobj, user.uri)
        if local:
            return Post(user, activity)
        else:
            return Reply(user, activity)

    elif atype in ["Announce", "Like"]:
        return Reaction(user, activity)

    elif atype == "Follow":
        return Follow(user, activity)

    elif atype == "Delete":
        return Delete(user, activity)

    return Activity(user, activity)
