from functools import wraps

from sanic import response,exceptions

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
            return response.json({'error': 'User not found', 'status_code': 404})

        kwargs["user"] = user
        return await handler(request, *args, **kwargs)
    return wrapper


def outbox_check(handler=None):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):

        data = await Outbox.find_one(dict(user_id=kwargs["user"].name, _id=kwargs["entity"]))
        if not data:
            raise exceptions.NotFound("Object not found")

        kwargs["entity"] = data
        return await handler(request, *args, **kwargs)
    return wrapper


def ui_app_check(handler=None):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        if request.app.ui_app_index and 'application/activity+json' not in request.headers.get(
                'Accept', ''):
            return await request.app.ui_app_index(request)
        else:
            return await handler(request, *args, **kwargs)
    return wrapper
