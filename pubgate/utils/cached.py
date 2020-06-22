from pubgate import BaseUrl
from pubgate.db import Inbox, User, Outbox
from pubgate.utils.networking import fetch


def cached_mode(request):
    if (request.args.get('cached')
            and request.app.config.get('APPLY_CASHING')):
        return True


async def ensure_inbox(object_id):
    # TODO also fetch and cache reactions (replies, likes, shares)
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


async def trace_replies(target):
    cls = Outbox if target.startswith(BaseUrl.value) else Inbox
    target_object = await cls.get_by_uri(target)
    is_reply = target_object.activity['object'].get('inReplyTo')
    if is_reply:
        await cls.cache.delete(is_reply)
        await trace_replies(is_reply)


async def handle_cache(activity, cls):
    target = None
    print(activity)
    if activity['type'] in ['Announce', 'Like']:
        target = activity['object']
    elif activity['type'] == 'Create' and activity['object'].get('inReplyTo'):
        target = activity['object']['inReplyTo']
    if target is None:
        return

    local = target.startswith(BaseUrl.value)
    if not local:
        await ensure_inbox(target)
    await cls.cache.delete(target)
    await trace_replies(target)
