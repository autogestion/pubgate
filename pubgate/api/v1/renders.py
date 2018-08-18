
from pubgate.api.v1.key import get_key


context = [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        {
            "Hashtag": "as:Hashtag",
            "sensitive": "as:sensitive"
        }
    ]


def user_profile(base_url, user_id):
    id = f"{base_url}/api/v1/user/{user_id}"

    return {
        "@context": context,
        "id": id,
        "type": "Person",
        "following": f"{id}/following",
        "followers": f"{id}/followers",
        "inbox": f"{base_url}/api/v1/inbox/{user_id}",
        "outbox": f"{base_url}/api/v1/outbox/{user_id}",
        "preferredUsername": f"{user_id}",
        "name": "",
        "summary": "<p></p>",
        "url": f"{base_url}/@{user_id}",
        "manuallyApprovesFollowers": False,
        "publicKey": get_key(id).to_dict(),
        "endpoints": {
            # "sharedInbox": f"{base_url}/inbox"
            "oauthTokenEndpoint": f"{base_url}/api/v1/auth/token"
        },
        "icon": {
            "type": "Image",
            "mediaType": "image/png",
            "url": "http://d1nhio0ox7pgb.cloudfront.net/_img/g_collection_png/standard/512x512/torii.png"
        }
    }


def ordered_collection(coll_id, data=None):
    collection = {
        "@context": context,
        "id": coll_id,
        "totalItems": len(data),
        "type": "OrderedCollection"
    }

    if data:
        collection["first"] = {
            "id": coll_id,
            "partOf": coll_id,
            "totalItems": len(data),
            "type": "OrderedCollectionPage",
            "orderedItems": data,
        }

    return collection
