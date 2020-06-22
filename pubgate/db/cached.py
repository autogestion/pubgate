from pubgate.renders import ordered_collection
from pubgate.db import Inbox, Outbox, Reactions


async def timeline_cached(cls, request, uri, user='stream'):
    filters = {
        "deleted": False,
        "activity.type": {'$in': ["Create", "Announce", "Like"]},
    }
    if user != 'stream':
        filters.update(cls.by_user(user))
    elif cls.__coll__ == 'inbox':
        filters.update(
            {"users.0": {"$ne": "cached"}, "users": {"$size": 1}}
        )

    page = request.args.get("page")
    if page:
        total = None
        page = int(page)
    else:
        total = await cls.count(filter=filters)
        page = 1

    limit = request.app.config.PAGINATION_LIMIT
    result = []
    if total != 0:
        data = await cls.find(filter=filters,
                              sort="activity.published desc",
                              skip=limit * (page - 1),
                              limit=limit)
        data = data.objects
        for entry in data:
            updated = await process_entry(entry.activity, request, cls.cache)
            result.append(updated)

    return ordered_collection(uri, total, page, result)


async def process_entry(activity, request, cache):
    ap_object = activity['object']
    if type(ap_object) == str:
        object_id = ap_object
    else:
        object_id = ap_object['id']
    cached = await cache.get(object_id)

    if cached:
        activity['object'] = cached
        return activity

    # Get details for boosted/liked object
    if isinstance(activity['object'], str):
        activity['object'] = await retrieve_object(
            request.app.base_url, activity['object']
        ) or activity['object']

    if isinstance(activity['object'], dict):
        # Get details for parent Object
        if activity['object'].get('inReplyTo') and \
                isinstance(activity['object']['inReplyTo'], str):
            activity['object']['inReplyTo'] = await retrieve_object(
                request.app.base_url, activity['object']['inReplyTo']
            ) or activity['object']['inReplyTo']

        # Get likes, reposts and replies
        # TODO make one aggregation query for all reactions
        await reaction_list(activity, request, 'replies', cache=cache)
        await reaction_list(activity, request, 'shares')
        await reaction_list(activity, request, 'likes')

    await cache.set(object_id, activity['object'])
    return activity


# TODO upgrade to get or cache for remote objects
async def retrieve_object(base_url, uri):
    if uri.startswith(base_url):
        result = await Outbox.get_by_uri(uri)
    else:
        result = await Inbox.get_by_uri(uri)

    if result:
        responce = result.activity['object']
        # responce['reactions'] = getattr(result, 'reactions', {})
        return responce
    return None


async def reaction_list(activity, request, reaction, cache=None):
    if (activity['object'].get(reaction)
            and isinstance(activity['object'][reaction], str)):
        activity['object'][reaction] = await getattr(
            Reactions, reaction
        )(
            request, activity['object']['id']
        ) or activity['object'][reaction]

        if (reaction == 'replies'
                and not isinstance(activity['object'][reaction], str)):
            if 'first' in activity['object'][reaction]:
                for reply in activity['object'][reaction]['first'].get('orderedItems', []):
                    await process_entry(reply, request, cache)
