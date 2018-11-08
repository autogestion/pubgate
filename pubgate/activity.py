from datetime import datetime

from pubgate.utils import random_object_id
from pubgate.db.models import Outbox, Inbox
from pubgate.networking import fetch


class FollowersMixin:

    async def recipients(self):
        result = await self.user.followers_get()
        return list(set(result))


class ReactionsMixin:

    async def recipients(self):
        followers = await self.user.followers_get()
        return list(set(followers + self.target))


class Activity:

    def __init__(self, user, activity):
        self.id = random_object_id()
        self.render = activity
        self.user = user
        activity["id"] = f"{user.uri}/activity/{self.id}"
        activity["actor"] = user.uri

    async def get_target(self, obj_id):
        target = await Inbox.get_by_object(obj_id)
        if not target:
            target = await fetch(obj_id)
        self.target = target["object"]["attributedTo"]
        return self.target

    @property
    def published(self):
        return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    async def save(self):
        await Outbox.save(self.user, self)


class Follow(Activity):

    async def recipients(self):
        return [self.render["object"]]


class Note(Activity, FollowersMixin):

    def __init__(self, user, activity):
        super().__init__(user, activity)
        activity["published"] = activity["object"]["published"] = self.published

        activity["to"] = activity["object"]["to"] = \
            ["https://www.w3.org/ns/activitystreams#Public"]
        activity["cc"] = activity["object"]["cc"] = [user.followers]

        activity["object"]["id"] = f"{user.uri}/object/{self.id}"
        activity["object"]["attributedTo"] = user.uri


class Reaction(Activity, ReactionsMixin):

    def __init__(self, user, activity):
        super().__init__(user, activity)
        activity["to"] = ["https://www.w3.org/ns/activitystreams#Public"]
        activity["cc"] = [user.followers, self.get_target(activity["object"])]


class Delete(FollowersMixin):
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
        if otype == "Note":
            return Note(user, activity)

    elif atype == "Follow":
        return Follow(user, activity)

    elif atype == "Delete":
        return Delete(user, activity)

    return Activity(user, activity)
