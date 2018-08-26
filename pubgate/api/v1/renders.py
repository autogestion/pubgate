
from pubgate.api.v1.key import get_key
from pubgate import LOGO

context = [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        {
            "Hashtag": "as:Hashtag",
            "sensitive": "as:sensitive"
        }
    ]


def user_profile(v1_path, user_id):
    actor_id = f"{v1_path}/user/{user_id}"

    return {
        "@context": context,
        "id": id,
        "type": "Person",
        "following": f"{actor_id}/following",
        "followers": f"{actor_id}/followers",
        "inbox": f"{v1_path}/inbox/{user_id}",
        "outbox": f"{v1_path}/outbox/{user_id}",
        "preferredUsername": f"{user_id}",
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
