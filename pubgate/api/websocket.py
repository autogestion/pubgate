import asyncio

import socketio
from sanic.log import logger
from sanic import Blueprint

ws = Blueprint('ws_v1')


sio = socketio.AsyncServer(async_mode='sanic', cors_allowed_origins=[])

class X:
    sockets = {}


@sio.event
async def connect(sid, environ):
    print('connect ', sid)
    await sio.emit('my event', {'data': 'foobar'})
    print(environ)
    await sio.emit('event', {'data': 'foobar2'}, room=sid)
    # z = environ['wsgi.input']
    # # zz = await z
    # print(z)
    # user_id = 'x'
    # sio.enter_room(sid, user_id)

    await sio.emit('my event', {'data': 'foobar'})


@sio.event
async def disconnect(sid):
    print('disconnect ', sid)

# @sio.event
# async def auth(sid, data):
#     print("-auth---------")
#     print(data)


# @sio.on('auth')
# def f1(sid, data):
#     print('auth2-----------------')
#     sio.emit('auth', 'auth', room=sid)
#     sio.emit('auth', 'auth')
#     sio.emit('ping1', 'pong', room=sid)
#     sio.emit('ping1', 'pong')
#     sio.emit('ping', 'pong1', room=sid)
#     sio.emit('ping', 'pong1')

@sio.on('ping')
def ping(sid, data):
    logger.warn('ping!')
    return 'panda', 13

@sio.on('panda')
def panda(sid, data):
    logger.warn('panda!')

@sio.on('panda')
def another_event(sid, data):
    print('ping-----------------')
    logger.debug('panda')
    sio.emit('panda', data, room=sid)
    sio.emit('panda', data)
    sio.emit('panda', 'fish')

#
# @ws.websocket('/socket')
# # @doc.summary("Returns user inbox, auth required")
# async def keep_alive(request, webs):
#
#         data = await webs.recv()
#         await webs.send('subscribed')
#         while True:
#             print(data)
#             await webs.send('update!')
#             await asyncio.sleep(5)
