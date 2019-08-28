from pubgate.renders import ordered_collection
from pubgate.db import Inbox, Outbox, Reactions


async def timeline_cached(cls, request, uri, user='stream'):

    page = request.args.get("page", 1)
    cache_key = f'{cls.__coll__}_{user}_{page}'
    data = await cls.cache.get(cache_key)
    if data:
        return data

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

    data = await get_ordered_cached(
        request, cls, filters, cls.activity_clean, uri
    )

    await cls.cache.set(cache_key, data)
    return data


async def get_ordered_cached(request, model, filters, cleaner, coll_id):
    page = request.args.get("page")

    if page:
        total = None
        page = int(page)
    else:
        total = await model.count(filter=filters)
        page = 1

    limit = request.app.config.PAGINATION_LIMIT
    if total != 0:
        print(filters)
        data = await model.find(filter=filters,
                                sort="activity.published desc",
                                skip=limit * (page - 1),
                                limit=limit)
        data = data.objects
        for entry in data:
            # Get details for boosted/liked object
            if isinstance(entry.activity['object'], str):
                entry.activity['object'] = await retrieve_object(
                    request.app.base_url, entry.activity['object']
                ) or entry.activity['object']

            if isinstance(entry.activity['object'], dict):
                # Get details for parent Object
                if entry.activity['object'].get('inReplyTo') and \
                        isinstance(entry.activity['object']['inReplyTo'], str):
                    entry.activity['object']['inReplyTo'] = await retrieve_object(
                        request.app.base_url, entry.activity['object']['inReplyTo']
                    ) or entry.activity['object']['inReplyTo']

                # Get likes, reposts and replies
                # TODO make one aggregation query for all reactions
                await reaction_list(entry, request, 'replies')
                await reaction_list(entry, request, 'shares')
                await reaction_list(entry, request, 'likes')

    else:
        data = []

    return ordered_collection(coll_id, total, page, cleaner(data))


# TODO upgrade to get or cache for remote objects
async def retrieve_object(base_url, uri):
    if uri.startswith(base_url):
        result = await Outbox.get_by_uri(uri)
    else:
        result = await Inbox.get_by_uri(uri)
    return result.activity['object'] if result else None


async def reaction_list(entry, request, reaction):
    if entry.activity['object'].get(reaction) and \
            isinstance(entry.activity['object'][reaction], str):
            entry.activity['object'][reaction] = await getattr(
                Reactions, reaction
            )(
                request, entry.activity['object']['id']
            ) or entry.activity['object'][reaction]
