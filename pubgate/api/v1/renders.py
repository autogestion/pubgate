from datetime import datetime

from pubgate.api.v1.crypto.key import get_key
from pubgate.api.v1.utils import random_object_id
from pubgate import LOGO

context = [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        {
            "Hashtag": "as:Hashtag",
            "sensitive": "as:sensitive",
            "toot": "http://joinmastodon.org/ns#",
            "featured": "toot:featured"
        }
    ]


class Activity:

    def __init__(self, v1_path, username, activity):
        self.obj_id = random_object_id()
        now = datetime.now()

        outbox_url = f"{v1_path}/outbox/{username}"
        user_id = f"{v1_path}/user/{username}"
        published = now.isoformat()

        activity["id"] = f"{outbox_url}/{self.obj_id}"
        activity["actor"] = user_id
        # activity["published"] = published
        if isinstance(activity["object"], dict):
            activity["object"]["id"] = f"{outbox_url}/{self.obj_id}/activity"
            # activity["object"]["published"] = published
            activity["object"]["attributedTo"] = user_id

        self.render = activity


class Actor:
    def __init__(self, user):

        self.domain = user.renders["domain"]
        self.v1_path = user.renders["v1_path"]
        self.username = user.username
        self.actor_id = f"{self.v1_path}/user/{user.username}"
        self.actor_type = user.actor_type

    @property
    def render(self):

        return {
            "@context": context,
            "id": self.actor_id,
            "type": self.actor_type,
            "following": f"{self.actor_id}/following",
            "followers": f"{self.actor_id}/followers",
            "inbox": f"{self.v1_path}/inbox/{self.username}",
            "outbox": f"{self.v1_path}/outbox/{self.username}",
            "preferredUsername": f"{self.username}",
            "name": "",
            "summary": "<p></p>",
            # "url": f"{base_url}/@{user_id}",
            "manuallyApprovesFollowers": False,
            "publicKey": get_key(self.actor_id).to_dict(),
            "endpoints": {
                # "sharedInbox": f"{base_url}/inbox"
                "oauthTokenEndpoint": f"{self.v1_path}/auth/token"
            },
            "icon": {
                "type": "Image",
                "mediaType": "image/png",
                "url": LOGO
            }
        }

    @property
    def webfinger(self):

        return {
            "subject": f"acct:{self.username}@{self.domain}",
            "aliases": [
                # "{method}://mastodon.social/@user",
                self.actor_id
            ],
            "links": [
                # {
                #     "rel": "http://webfinger.net/rel/profile-page",
                #     "type": "text/html",
                #     "href": "{method}://mastodon.social/@user"
                # },

                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": self.actor_id
                },
                {
                    "rel": "magic-public-key",
                    "href": get_key(self.username).to_magic_key()
                },
                # {
                #     "rel": "salmon",
                #     "href": "{method}://mastodon.social/api/salmon/285169"
                # },

                # {
                #     "rel": "http://ostatus.org/schema/1.0/subscribe",
                #     "template": "{method}://mastodon.social/authorize_follow?acct={uri}"
                # }
            ]
        }


def ordered_collection(coll_id, total, page, data):
    collection = {
        "@context": context
    }

    collection_page = {
        "id": f"{coll_id}?page={page}",
        "partOf": coll_id,
        "totalItems": len(data),
        "type": "OrderedCollectionPage",
        "orderedItems": data,
    }
    if data:
        collection["next"] = f"{coll_id}?page={page + 1}"

    if total:
        collection.update({
            "id": coll_id,
            "totalItems": total,
            "type": "OrderedCollection",
        })
        if data:
            collection["first"] = collection_page

    else:
        collection.update(collection_page)

    return collection

