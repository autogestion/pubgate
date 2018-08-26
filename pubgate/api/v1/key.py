import binascii
import os
from typing import Callable
import re
import base64
import hashlib
from urllib.parse import urlparse
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

from little_boxes.key import Key
from sanic.log import logger

from pubgate import KEY_DIR


def _new_key() -> str:
    return binascii.hexlify(os.urandom(32)).decode("utf-8")


def get_secret_key(name: str, new_key: Callable[[], str] = _new_key) -> str:
    """Loads or generates a cryptographic key."""
    key_path = os.path.join(KEY_DIR, f"{name}.key")
    if not os.path.exists(key_path):
        k = new_key()
        with open(key_path, "w+") as f:
            f.write(k)
        return k

    with open(key_path) as f:
        return f.read()


def get_key(owner: str) -> Key:
    """"Loads or generates an RSA key."""
    k = Key(owner)
    user = re.sub('[^\w\d]', "_", owner)
    key_path = os.path.join(KEY_DIR, f"key_{user}.pem")
    if os.path.isfile(key_path):
        with open(key_path) as f:
            privkey_pem = f.read()
            k.load(privkey_pem)
    else:
        k.new()
        with open(key_path, "w") as f:
            f.write(k.privkey_pem)

    return k


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
