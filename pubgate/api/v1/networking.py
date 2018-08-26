import aiohttp
import base64
import json

from sanic.log import logger
from sanic import exceptions
from little_boxes.linked_data_sig import generate_signature
from little_boxes.httpsig import _parse_sig_header, _body_digest, _build_signed_string, _verify_h
from little_boxes.key import Key

from pubgate import __version__
from pubgate.api.v1.utils import make_label
from pubgate.api.v1.renders import context
from pubgate.api.v1.key import get_key, HTTPSigAuth


async def verify_request(method: str, path: str, headers, body: str) -> bool:
    hsig = _parse_sig_header(headers.get("Signature"))
    if not hsig:
        logger.debug("no signature in header")
        return False
    logger.debug(f"hsig={hsig}")
    signed_string = _build_signed_string(
        hsig["headers"], method, path, headers, _body_digest(body)
    )

    actor = await fetch(hsig["keyId"])
    if not actor: return False
    k = Key(actor["id"])
    k.load_pub(actor["publicKey"]["publicKeyPem"])
    if k.key_id() != hsig["keyId"]:
        return False

    return _verify_h(signed_string, base64.b64decode(hsig["signature"]), k.pubkey)


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"accept": 'application/activity+json',
                                              "user-agent": f"PubGate v:{__version__}"}
                                ) as resp:
            logger.info(f"Fetch {url}, status: {resp.status}, {resp.reason}")
            return await resp.json()


async def deliver_task(recipient, http_sig, activity):
    async with aiohttp.ClientSession() as session:
        async with session.get(recipient,
                               headers={'Accept': 'application/activity+json',
                                        "User-Agent": f"PubGate v:{__version__}",}
                               ) as resp:
            logger.info(f"Delivering {make_label(activity)} ===>> {recipient},"
                        f" status: {resp.status}, {resp.reason}")
            profile = await resp.json()

    body = json.dumps(activity)
    url = profile["inbox"]
    headers = http_sig.sign(url, body)

    async with aiohttp.ClientSession() as session:
        async with session.post(url,
                                data=body,
                                headers=headers) as resp:
            logger.info(f"Post to inbox {resp.real_url}, status: {resp.status}, {resp.reason}")
            # print(resp.request_info.headers)
            print("\n")


async def deliver(activity, recipients):
    # TODO retry over day if fails
    key = get_key(activity["actor"])
    activity['@context'] = context
    generate_signature(activity, key)

    headers = {"content-type": 'application/activity+json',
               "user-agent": f"PubGate v:{__version__}"}

    http_sig = HTTPSigAuth(key, headers)
    # print(activity)

    for recipient in recipients:
        # try:
            await deliver_task(recipient, http_sig, activity)
        # except Exception as e:
        #     logger.error(e)
