from functools import wraps

from sanic import exceptions

from pubgate.db import User, Outbox


def token_check(handler=None):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        user = await User.find_one(dict(name=kwargs["user"].lower(),
                                        token=request.token))
        if not user:
            raise exceptions.Unauthorized("Auth required.")

        kwargs["user"] = user
        return await handler(request, *args, **kwargs)
    return wrapper


def user_check(handler=None):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        user = await User.find_one(dict(name=kwargs["user"].lower()))
        if not user:
            raise exceptions.NotFound("User not found")

        kwargs["user"] = user
        return await handler(request, *args, **kwargs)
    return wrapper


def outbox_check(handler=None):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):

        data = await Outbox.get(dict(user_id=kwargs["user"].name, _id=kwargs["entity"]))
        if not data:
            raise exceptions.NotFound("Object not found")

        kwargs["entity"] = data
        return await handler(request, *args, **kwargs)
    return wrapper
