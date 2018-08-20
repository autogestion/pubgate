import binascii
import os
from functools import wraps

from sanic import exceptions

from pubgate.api.v1.db.models import User


def make_label(activity):
    label = activity["type"]
    if isinstance(activity["object"], dict):
        label = f'{label}: {activity["object"]["type"]}'
    return label


def random_object_id() -> str:
    """Generates a random object ID."""
    return binascii.hexlify(os.urandom(8)).decode("utf-8")


def auth_required(handler=None):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        user = await User.find_one(dict(username=kwargs["user_id"],
                                        token=request.token))
        if not user:
            raise exceptions.Unauthorized("Auth required.")

        return await handler(request, *args, **kwargs)
    return wrapper
