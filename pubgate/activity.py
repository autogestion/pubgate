import asyncio
from datetime import datetime
from sanic.exceptions import SanicException

from pubgate.utils import random_object_id
from pubgate.utils.networking import deliver
from pubgate.utils import check_origin
from pubgate.db import Outbox, Inbox


class BaseActivity:
    def __init__(self, user, activity):
        activity.pop("bto", None)
        activity.pop("bcc", None)
        self.render = activity
        self.user = user
        self.cc = activity.get("cc", [])[:]
        activity["actor"] = user.uri

    async def recipients(self):
        result = await self.user.followers_get()
        result.extend(self.cc)
        return list(set(result))

    async def deliver(self, debug=False):
        recipients = await self.recipients()
        asyncio.ensure_future(deliver(
            self.user.key, self.render, recipients, debug=debug))


class Activity(BaseActivity):

    def __init__(self, user, activity):
        super().__init__(user, activity)
        self.id = random_object_id()
        activity["id"] = f"{user.uri}/activity/{self.id}"

    @staticmethod
    def published():
        return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    async def save(self, **kwargs):
        await Outbox.save(self, **kwargs)


class Follow(Activity):

    async def recipients(self):
        return [self.render["object"]]

    async def save(self, **kwargs):
        filters = self.user.follow_filter(Inbox)
        filters["activity.object.object"] = self.render["object"]
        followed = await Inbox.find_one(filters)
        if followed:
            raise SanicException('This user is already followed', status_code=409)

        await Outbox.save(self, **kwargs)


class Create(Activity):

    def __init__(self, user, activity):
        super().__init__(user, activity)
        if "published" not in activity:
            activity["published"] = activity["object"]["published"] = self.published()

        # TODO iplement filtering of public and non-public posts in timelines
        # https://www.w3.org/TR/activitypub/#public-addressing

        activity["to"] = activity["object"]["to"] = \
            ["https://www.w3.org/ns/activitystreams#Public"]

        activity["object"]["id"] = f"{user.uri}/object/{self.id}"
        activity["object"]["attributedTo"] = user.uri
        activity["object"]["replies"] = f"{user.uri}/object/{self.id}/replies"
        activity["object"]["likes"] = f"{user.uri}/object/{self.id}/likes"
        activity["object"]["shares"] = f"{user.uri}/object/{self.id}/shares"

        check = activity.get("cc", None)
        if check:
            activity["cc"].insert(0, user.followers)
        else:
            activity["cc"] = [user.followers]
        activity["object"]["cc"] = activity["cc"]


class Reaction(Activity):
    def __init__(self, user, activity):
        super().__init__(user, activity)
        check = activity.get("cc", None)
        if check:
            activity["cc"].insert(0, user.followers)
        else: activity["cc"] = [user.followers]
        activity["published"] = self.published()
        activity["to"] = ["https://www.w3.org/ns/activitystreams#Public"]

    async def save(self):
        local = check_origin(self.render["object"], self.render["actor"])
        await Outbox.reaction_add(self, local)


class Unfollow(BaseActivity):
    async def recipients(self):
        return [self.render["object"]["object"]]

    async def save(self):
        await Outbox.unfollow(self)


class Delete(BaseActivity):
    # TODO check if post have mentions to add to recipients
    def __init__(self, user, activity):
        super().__init__(user, activity)
        activity["to"] = ["https://www.w3.org/ns/activitystreams#Public"]

    async def save(self):
        await Outbox.delete(self.render["object"]["id"])

    @classmethod
    def construct(cls, user, obj_id):
        return cls(user, {
            "id": f"{obj_id}#delete",
            "type": "Delete",
            "object": {
                "id": obj_id,
                "type": "Tombstone"
            }
        })


class UndoReaction(Delete):
    async def save(self):
        await Outbox.reaction_undo(self)


def choose(user, activity):
    # TODO add support for Collections (Add, Remove), Update, Block
    atype = activity.get("type", None)
    otype = None
    aobj = activity.get("object", None)
    if aobj and isinstance(aobj, dict):
        otype = aobj.get("type", None)

    if atype == "Create":
        return Create(user, activity)

    elif atype in ["Announce", "Like"]:
        return Reaction(user, activity)

    elif atype == "Follow":
        return Follow(user, activity)

    elif atype == "Undo":
        if otype == "Follow":
            return Unfollow(user, activity)
        elif otype in ["Announce", "Like"]:
            return UndoReaction(user, activity)

    elif atype == "Delete":
        # TODO Replaces deleted object with a Tombstone object
        return Delete(user, activity)

    return Activity(user, activity)
