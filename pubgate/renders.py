

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

        actor = self.user.profile
        actor.update({
            "@context": context,
            "id": self.user.uri,
            "following": self.user.following,
            "followers": self.user.followers,
            "inbox": self.user.inbox,
            "outbox": self.user.outbox,
            "name": "",
            # "url": f"{base_url}/@{user_id}",
            "manuallyApprovesFollowers": False,
            "publicKey": self.user.key.to_dict(),
            "endpoints": {
                # "sharedInbox": f"{base_url}/inbox"
                "oauthTokenEndpoint": f"{self.user.uri}/token"
            }
        })
        return actor

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
                    "href": self.user.key.to_magic_key()
                },
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

