import aiohttp
import json

from sanic.log import logger

from pubgate import __version__
from pubgate.utils import make_label
from pubgate.renders import context
from pubgate.crypto.httpsig import HTTPSigAuth, verify
from pubgate.crypto.httpsig import _parse_sig_header
# from pubgate.crypto.datasig import generate_signature


async def verify_request(request) -> bool:
    hsig = _parse_sig_header(request.headers.get("Signature"))
    if not hsig:
        return False
    actor = await fetch(hsig["keyId"])
    if not actor:
        return False

    return verify(hsig, request, actor)


async def fetch(url, pass_through=False):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"accept": 'application/activity+json',
                                             "user-agent": f"PubGate v:{__version__}"}
                                ) as resp:
            status_code = resp.status
            logger.info(f"Fetch {url}, status: {resp.status}, {resp.reason}")
            try:
                result = await resp.json(encoding='utf-8')
            except aiohttp.ContentTypeError as e:
                result = {'fetch_error': await resp.text()}
                status_code = 500
                failed = e

            if pass_through:
                return status_code, result
            elif failed:
                raise e
            return await result


async def fetch_text(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"accept": 'application/activity+json',
                                             "user-agent": f"PubGate v:{__version__}"}
                               ) as resp:
            logger.info(f"Fetch {url}, status: {resp.status}, {resp.reason}")
            return await resp.text()


async def deliver_task(recipient, http_sig, activity, debug=False):
    logger.info(f"Delivering {make_label(activity)} ===>> {recipient}")

    profile = await fetch(recipient)
    url = profile["inbox"]
    body = json.dumps(activity)
    headers = http_sig.sign(url, body)

    async with aiohttp.ClientSession() as session:
        async with session.post(url,
                                data=body,
                                headers=headers) as resp:
            logger.info(f"Post to inbox {resp.real_url}, status: {resp.status}, {resp.reason}")
            if debug:
                from pprint import pprint
                pprint(activity)
                print(resp.request_info.headers)
            # print(resp.request_info.headers)
            print("\n")


async def deliver(key, activity, recipients, debug=False):
    # TODO retry over day if fails
    if '@context' not in activity:
        activity['@context'] = context
    # TODO investigate is it necessary to sign object
    # TODO investigate is it necessary to use pyld instead of json.dump
    # if "signature" not in activity:
    #     generate_signature(activity, key)

    headers = {"content-type": "application/activity+json",
               "user-agent": f"PubGate v:{__version__}"}

    http_sig = HTTPSigAuth(key, headers)

    for recipient in recipients:
        try:
            await deliver_task(recipient, http_sig, activity, debug=debug)
        except Exception as e:
            logger.error(e)
