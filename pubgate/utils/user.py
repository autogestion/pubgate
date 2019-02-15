import asyncio

from pubgate.crypto.key import get_key
from pubgate.utils.networking import deliver


class UserUtils:

    @property
    def key(self):
        return get_key(self.alias)

    @property
    def following(self): return f"{self.uri}/following"

    @property
    def followers(self): return f"{self.uri}/followers"

    @property
    def inbox(self): return f"{self.uri}/inbox"

    @property
    def outbox(self): return f"{self.uri}/outbox"

    @property
    def liked(self): return f"{self.uri}/liked"

    async def forward_to_followers(self, activity):
        recipients = await self.followers_get()
        try:
            recipients.remove(activity["actor"])
        except ValueError:
            pass
        asyncio.ensure_future(deliver(self.key, activity, recipients))
