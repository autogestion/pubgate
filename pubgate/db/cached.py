from pubgate.renders import ordered_collection
from pubgate.db import Inbox, Outbox, Reactions

cache = Outbox.cache


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
        counter = 0
        for entry in data:
            counter += 1
            updated = await process_entry(entry.activity, request)
            result.append(updated)

    return ordered_collection(uri, total, page, result)


async def process_entry(activity, request):
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
        activity['object'] = await retrieve_object(activity['object'], request)\
                             or activity['object']

    if isinstance(activity['object'], dict):
        # Get details for parent Object
        if activity['object'].get('inReplyTo') and \
                isinstance(activity['object']['inReplyTo'], str):
            activity['object']['inReplyTo'] = \
                await retrieve_object(activity['object']['inReplyTo'],
                                      request, in_reply=True)\
                or activity['object']['inReplyTo']

    # Get likes, reposts and replies
    # TODO make one aggregation query for all reactions
    await reaction_list(activity, request)
    await cache.set(object_id, activity['object'])
    return activity


# TODO upgrade to get or cache for remote objects
async def retrieve_object(uri, request, in_reply=False):
    cached = await cache.get(uri)
    if cached: return cached

    if uri.startswith(request.app.base_url):
        result = await Outbox.get_by_uri(uri)
    else:
        result = await Inbox.get_by_uri(uri)

    if result:
        # if in_reply:
        #     await reaction_list(result.activity, request,
        #                         skip_recursion=True)
        # else:
        #     await process_entry(result.activity, request)
        return result.activity['object']

    return None


async def reaction_list(activity, request, skip_recursion=False):
    for reaction in ['replies', 'shares', 'likes']:
        have_reaction = activity['object'].get(reaction)
        if not have_reaction or isinstance(activity['object'][reaction], str):
            activity['object'][reaction] = await getattr(Reactions, reaction)(
                request, activity['object']['id']
            )

        if (reaction == 'replies'
                and not skip_recursion
                and 'first' in activity['object'][reaction]):
            for reply in activity['object'][reaction]['first']\
                    .get('orderedItems', []):
                await process_entry(reply, request)
