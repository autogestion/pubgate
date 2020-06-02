import asyncio

import socketio
from sanic import Blueprint

ws = Blueprint('ws_v1')

sio = socketio.AsyncServer(async_mode='sanic')

class X:
    sockets = {}


@sio.event
async def connect(sid, environ):
    print('connect ', sid)
    print(environ)
    z = environ['wsgi.input']
    # zz = await z
    print(z)
    user_id = 'x'
    sio.enter_room(sid, user_id)

@sio.event
async def disconnect(sid):
    print('disconnect ', sid)

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
