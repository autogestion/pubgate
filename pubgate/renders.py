
from pubgate.crypto.key import get_key
from pubgate import LOGO


context = [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        {
            "Hashtag": "as:Hashtag",
            "sensitive": "as:sensitive"
            # "toot": "http://joinmastodon.org/ns#",
            # "featured": "toot:featured"
        }
    ]


class Actor:
    def __init__(self, user):
        self.user = user

    @property
    def render(self):

        return {
            "@context": context,
            "id": self.user.uri,
            "type": self.user.actor_type,
            "following": self.user.following,
            "followers": self.user.followers,
            "inbox": self.user.inbox,
            "outbox": self.user.outbox,
            "preferredUsername": f"{self.user.name}",
            "name": "",
            "summary": "<p></p>",
            # "url": f"{base_url}/@{user_id}",
            "manuallyApprovesFollowers": False,
            "publicKey": get_key(self.user.uri).to_dict(),
            "endpoints": {
                # "sharedInbox": f"{base_url}/inbox"
                # "oauthTokenEndpoint": f"{self.base_url}/auth/token"
            },
            "icon": {
                "type": "Image",
                "mediaType": "image/png",
                "url": LOGO
            }
        }

    def webfinger(self, resource):

        return {
            "subject": resource,
            "aliases": [
                # "{method}://mastodon.social/@user",
                self.user.uri
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
                    "href": self.user.uri
                },
                {
                    "rel": "magic-public-key",
                    "href": get_key(self.user.uri).to_magic_key()
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

