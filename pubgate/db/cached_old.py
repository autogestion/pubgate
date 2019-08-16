
async def get_ordered_cached_fast(request, model, filters, cleaner, coll_id):
    page = request.args.get("page")

    if page:
        total = None
        page = int(page)
    else:
        total = await model.count(filter=filters)
        page = 1

    limit = request.app.config.PAGINATION_LIMIT
    if total != 0:
        data = await model.find(filter=filters,
                                sort="activity.published desc",
                                skip=limit * (page - 1),
                                limit=limit)
        data = data.objects

        get_cached_inbox, get_cached_outbox, get_cached_index = [], [], []
        for index, entry in enumerate(data):
            if entry.activity['type'] in ["Announce", "Like"] and \
                    isinstance(entry.activity['object'], str):
                if entry.activity['object'].startswith(request.app.base_url):
                    get_cached_outbox.append(entry.activity['object'])
                else:
                    get_cached_inbox.append(entry.activity['object'])
                get_cached_index.append(index)

        if get_cached_inbox:
            get_cached_inbox = await Inbox.find(
                filter={"activity.object.id": {'$in': get_cached_inbox}}
            )
            get_cached_inbox = get_cached_inbox.objects

        if get_cached_outbox:
            get_cached_outbox = await Outbox.find(
                filter={"activity.object.id": {'$in': get_cached_outbox}}
            )
            get_cached_outbox = get_cached_outbox.objects

        get_cached = get_cached_inbox + get_cached_outbox

        ref_activity_dict = {
            x['activity']['object']['id']: x['activity']['object'] for x in get_cached
        }
        for index in get_cached_index:
            obj_id = data[index].activity['object']
            data[index].activity['object'] = ref_activity_dict.get(obj_id, obj_id)

    else:
        data = []

    return ordered_collection(coll_id, total, page, cleaner(data))