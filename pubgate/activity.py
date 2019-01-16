import asyncio
from datetime import datetime

from pubgate.utils import random_object_id
from pubgate.utils.networking import deliver
from pubgate.db import Outbox


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

    @property
    def published(self):
        return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    async def save(self, **kwargs):
        await Outbox.save(self, **kwargs)


class Follow(Activity):

    async def recipients(self):
        return [self.render["object"]]


class Create(Activity):

    def __init__(self, user, activity):
        super().__init__(user, activity)
        if "published" not in activity:
            activity["published"] = activity["object"]["published"] = self.published

        activity["to"] = activity["object"]["to"] = \
            ["https://www.w3.org/ns/activitystreams#Public"]

        activity["object"]["id"] = f"{user.uri}/object/{self.id}"
        activity["object"]["attributedTo"] = user.uri

        check = activity.get("cc", None)
        if check:
            activity["cc"].insert(0, user.followers)
        else: activity["cc"] = [user.followers]
        activity["object"]["cc"] = activity["cc"]


class Reaction(Activity):
    def __init__(self, user, activity):
        super().__init__(user, activity)
        check = activity.get("cc", None)
        if check:
            activity["cc"].insert(0, user.followers)
        else: activity["cc"] = [user.followers]
        activity["published"] = self.published
        activity["to"] = ["https://www.w3.org/ns/activitystreams#Public"]


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


def choose(user, activity):
    # TODO add support for Add, Remove, Update
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
            return Delete(user, activity)

    elif atype == "Delete":
        # TODO Replaces deleted object with a Tombstone object
        return Delete(user, activity)

    return Activity(user, activity)
