from functools import wraps

from sanic import exceptions

from pubgate.db.user import User


def token_check(handler=None):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        user = await User.find_one(dict(name=kwargs["user"],
                                        token=request.token))
        if not user:
            raise exceptions.Unauthorized("Auth required.")

        kwargs["user"] = user
        return await handler(request, *args, **kwargs)
    return wrapper


def user_check(handler=None):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        user = await User.find_one(dict(name=kwargs["user"]))
        if not user:
            raise exceptions.Unauthorized("Incorrect username.")

        kwargs["user"] = user
        return await handler(request, *args, **kwargs)
    return wrapper


