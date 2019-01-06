import asyncio

class Streams:
    def __init__(self):
        self.inbox = asyncio.Queue()
        self.outbox = asyncio.Queue()
