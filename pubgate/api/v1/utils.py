import binascii
import os
import aiohttp
from functools import wraps
from aiohttp.client_reqrep import ClientRequest
from urllib.parse import urlsplit

from sanic.log import logger
from sanic import exceptions
from little_boxes.httpsig import _build_signed_string
from little_boxes.linked_data_sig import generate_signature

from pubgate import __version__
from pubgate.api.v1.db.models import User

import base64
import hashlib
from datetime import datetime
from urllib.parse import urlparse

from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5


class HTTPSigAuth:
    """Requests auth plugin for signing requests on the fly."""

    def __init__(self, key) -> None:
        self.key = key

    def __call__(self, r):
        logger.info(f"keyid={self.key.key_id()}")
        host = urlparse(str(r.url)).netloc

        bh = hashlib.new("sha256")
        body = r.body
        try:
            body = r.body.encode("utf-8")
        except AttributeError:
            pass
        bh.update(body)
        bodydigest = "SHA-256=" + base64.b64encode(bh.digest()).decode("utf-8")

        date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        r.headers.update({"Digest": bodydigest, "Date": date, "Host": host})

        sigheaders = "(request-target) user-agent host date digest content-type"

        to_be_signed = _build_signed_string(
            sigheaders, r.method, r.path_url, r.headers, bodydigest
        )
        signer = PKCS1_v1_5.new(self.key.privkey)
        digest = SHA256.new()
        digest.update(to_be_signed.encode("utf-8"))
        sig = base64.b64encode(signer.sign(digest))
        sig = sig.decode("utf-8")

        key_id = self.key.key_id()
        headers = {
            "Signature": f'keyId="{key_id}",algorithm="rsa-sha256",headers="{sigheaders}",signature="{sig}"'
        }
        logger.debug(f"signed request headers={headers}")

        r.headers.update(headers)

        return r


class PGClientRequest(ClientRequest):
    def update_auth(self, auth):
        auth(self)

    @property
    def path_url(self):
        """Build the path URL to use."""

        url = []

        p = urlsplit(str(self.url))

        path = p.path
        if not path:
            path = '/'

        url.append(path)

        query = p.query
        if query:
            url.append('?')
            url.append(query)

        return ''.join(url)


async def deliver_task(recipient, **kwargs):
    logger.info(f" Delivering {make_label(kwargs['json'])} ===> {recipient}")
    async with aiohttp.ClientSession() as session:
        async with session.get(recipient,
                               headers={'Accept': 'application/activity+json'}
                               ) as resp:
            logger.info(resp)
            profile = await resp.json()

    async with aiohttp.ClientSession(request_class=PGClientRequest) as session:
        async with session.post(profile["inbox"], **kwargs) as resp:
            logger.info(resp)


async def deliver(activity, recipients, key):
    # TODO deliver
    # TODO retry over day if fails

    generate_signature(activity, key)
    kwargs = dict(json=activity,
                  auth=HTTPSigAuth(key),
                  headers={
                        'Accept': 'application/activity+json',
                        "Content-Type": 'application/activity+json',
                        "User-Agent": f"Pubgate v:{__version__}",
                  })

    for recipient in recipients:
        # try:
            await deliver_task(recipient, **kwargs)
        # except Exception as e:
        #     logger.error(e)


def make_label(activity):
    label = activity["type"]
    if isinstance(activity["object"], dict):
        label = f'{label}: {activity["object"]["type"]}'
    return label


def random_object_id() -> str:
    """Generates a random object ID."""
    return binascii.hexlify(os.urandom(8)).decode("utf-8")


def auth_required(handler=None):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        user = await User.find_one(dict(username=kwargs["user_id"],
                                        token=request.token))
        if not user:
            raise exceptions.Unauthorized("Auth required.")

        return await handler(request, *args, **kwargs)
    return wrapper
