from datetime import datetime

from pubgate.api.v1.key import get_key
from pubgate.api.v1.utils import random_object_id
from pubgate import LOGO

context = [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        {
            "Hashtag": "as:Hashtag",
            "sensitive": "as:sensitive"
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
        activity["published"] = published
        if isinstance(activity["object"], dict):
            activity["object"]["id"] = f"{outbox_url}/{self.obj_id}/activity"
            activity["object"]["published"] = published
            activity["object"]["attributedTo"] = user_id

        self.render = activity


class Actor:
    def __init__(self, v1_path, username, actor_type):
        actor_id = f"{v1_path}/user/{username}"

        self.render = {
            "@context": context,
            "id": actor_id,
            "type": actor_type,
            "following": f"{actor_id}/following",
            "followers": f"{actor_id}/followers",
            "inbox": f"{v1_path}/inbox/{username}",
            "outbox": f"{v1_path}/outbox/{username}",
            "preferredUsername": f"{username}",
            "name": "",
            "summary": "<p></p>",
            # "url": f"{base_url}/@{user_id}",
            "manuallyApprovesFollowers": False,
            "publicKey": get_key(actor_id).to_dict(),
            "endpoints": {
                # "sharedInbox": f"{base_url}/inbox"
                "oauthTokenEndpoint": f"{v1_path}/auth/token"
            },
            "icon": {
                "type": "Image",
                "mediaType": "image/png",
                "url": LOGO
            }
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



