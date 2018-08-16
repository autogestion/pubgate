import binascii
import os
import aiohttp

from sanic.log import logger


async def deliver_task(recipient, activity):
    async with aiohttp.ClientSession() as session:

        async with session.get(recipient,
                               headers={'Accept': 'application/activity+json'}
                               ) as resp:
            logger.info(resp)
            profile = await resp.json()

        async with session.post(profile["inbox"],
                                json=activity,
                                headers={'Accept': 'application/activity+json'}
                                ) as resp:
            logger.info(resp)


async def deliver(activity, recipients):
    # TODO deliver
    # TODO sign object
    # TODO retry over day if fails
    for recipient in recipients:
        try:
            await deliver_task(recipient, activity)
        except Exception as e:
            logger.error(e)


def make_label(activity):
    label = activity["type"]
    if isinstance(activity["object"], dict):
        label = f'{label}: {activity["object"]["type"]}'
    return label


def random_object_id() -> str:
    """Generates a random object ID."""
    return binascii.hexlify(os.urandom(8)).decode("utf-8")