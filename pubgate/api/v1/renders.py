
from little_boxes.key import Key


context = [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        {
            "Hashtag": "as:Hashtag",
            "sensitive": "as:sensitive"
        }
    ]


def user_profile(base_url, user_id):
    key = Key(f"{base_url}/user/{user_id}")
    key.new()

    return {
        "@context": context,
        "id": f"{base_url}/api/v1/user/{user_id}",
        "type": "Person",
        "following": f"{base_url}/user/{user_id}/following",
        "followers": f"{base_url}/user/{user_id}/followers",
        "inbox": f"{base_url}/inbox/{user_id}/inbox",
        "outbox": f"{base_url}/outbox/{user_id}/outbox",
        "preferredUsername": f"{user_id}",
        "name": "",
        "summary": "<p></p>",
        "url": f"{base_url}/@{user_id}",
        "manuallyApprovesFollowers": False,
        "publicKey": key.to_dict(),
        "tag": [],
        "attachment": [],
        "endpoints": {
            "sharedInbox": f"{base_url}/inbox"
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
