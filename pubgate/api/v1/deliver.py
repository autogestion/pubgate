import aiohttp
import base64
import hashlib
from urllib.parse import urlparse
import json

from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

from sanic.log import logger
from sanic import exceptions
from little_boxes.linked_data_sig import generate_signature

from pubgate import __version__
from pubgate.api.v1.utils import make_label
from pubgate.api.v1.renders import context
from pubgate.api.v1.key import get_key


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
            print(resp.request_info.headers)
            print("\n")


async def deliver(activity, recipients):
    # TODO deliver
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


class HTTPSigAuth:
    """Requests auth plugin for signing requests on the fly."""

    def __init__(self, key, headers) -> None:
        self.key = key
        self.headers = headers

    def sign(self, url, r_body):
        logger.info(f"keyid={self.key.key_id()}")
        host = urlparse(url).netloc
        headers = self.headers.copy()

        bh = hashlib.new("sha256")
        body = r_body
        try:
            body = r_body.encode("utf-8")
        except AttributeError:
            pass
        bh.update(body)
        bodydigest = "SHA-256=" + base64.b64encode(bh.digest()).decode("utf-8")

        headers.update({"digest": bodydigest, "host": host})

        sigheaders = "host digest"
        out = []
        for signed_header in sigheaders.split(" "):
            if signed_header == "digest":
                out.append("digest: " + bodydigest)
            else:
                out.append(signed_header + ": " + headers[signed_header])
        to_be_signed = "\n".join(out)

        signer = PKCS1_v1_5.new(self.key.privkey)
        digest = SHA256.new()
        digest.update(to_be_signed.encode("utf-8"))
        sig = base64.b64encode(signer.sign(digest))
        sig = sig.decode("utf-8")

        key_id = self.key.key_id()
        headers.update({
            "Signature": f'keyId="{key_id}",algorithm="rsa-sha256",headers="{sigheaders}",signature="{sig}"'
        })
        logger.debug(f"signed request headers={headers}")

        return headers
