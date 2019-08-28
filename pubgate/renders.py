

context = "https://www.w3.org/ns/activitystreams"


class Actor:
    def __init__(self, user):
        self.user = user

    def render(self, base_url):

        actor = self.user.profile
        actor.update({
            "@context": context,
            "preferredUsername": self.user.name,
            "id": self.user.uri,
            "following": self.user.following,
            "followers": self.user.followers,
            "inbox": self.user.inbox,
            "outbox": self.user.outbox,
            "liked": self.user.liked,
            "url": self.user.uri,
            "manuallyApprovesFollowers": False,
            "publicKey": self.user.key.to_dict(),
            "endpoints": {
                # "sharedInbox": f"{base_url}/inbox"
                "oauthTokenEndpoint": f"{base_url}/token"
            }
        })
        return actor

    def webfinger(self, resource):

        return {
            "subject": resource,
            "aliases": [
                self.user.alias,
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
                }
                # {
                #     "rel": "magic-public-key",
                #     "href": self.user.key.to_magic_key()
                # },
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

