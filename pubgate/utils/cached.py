from pubgate.db import Inbox, User
from pubgate.utils.networking import fetch


async def ensure_cached(object_id):
    exists = await Inbox.get_by_uri(object_id)
    if not exists:
        cached_user = await User.find_one({'name': 'cached'})
        activity_object = await fetch(object_id)
        await Inbox.save(cached_user, {
            'type': 'Create',
            'id': f'{object_id}#activity',
            'published': activity_object['published'],
            'object': activity_object
        })