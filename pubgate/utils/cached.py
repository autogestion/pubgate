from pubgate import BaseUrl
from pubgate.db import Inbox, User, Outbox
from pubgate.utils.networking import fetch

def cached_mode(request):
    if (request.args.get('cached')
            and request.app.config.get('APPLY_CASHING')):
        return True


async def ensure_inbox(object_id):
    # TODO also fetch and cache reactions (replies, likes, shares)
    print('ensure_inbox_started')
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


async def drop_cache(target):
    #cache manager is same for both Inbox and Outbox
    await Outbox.cache.delete(target)
    local = target.startswith(BaseUrl.value)
    if not local:
        await ensure_inbox(target)


async def trace_replies(target):
    cls = Outbox if target.startswith(BaseUrl.value) else Inbox
    target_object = await cls.get_by_uri(target)
    print('target_object')
    print(target)
    print(target_object)
    is_reply = target_object.activity['object'].get('inReplyTo')
    print(is_reply)
    if is_reply:
        await drop_cache(is_reply)
        await trace_replies(is_reply)


async def clear_cache(activity, cls):
    target = None
    print(activity)
    if activity['type'] in ['Announce', 'Like']:
        target = activity['object']
    elif activity['type'] == 'Create' and activity['object'].get('inReplyTo'):
        target = activity['object']['inReplyTo']
    if target is None:
        return

    await drop_cache(target, cls)
    await trace_replies(target, cls)
