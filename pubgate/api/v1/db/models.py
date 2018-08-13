
from sanic_motor import BaseModel


class User(BaseModel):
    __coll__ = 'users'
    __unique_fields__ = ['username']


class Outbox(BaseModel):
    __coll__ = 'outbox'
    __unique_fields__ = ['_id']


class Inbox(BaseModel):
    __coll__ = 'inbox'
    __unique_fields__ = ['_id']
