"""

Mastodon instances won't accept requests that are not signed using this scheme.

"""
import base64
import hashlib
import logging
from typing import Any
from typing import Dict
from typing import Optional
from urllib.parse import urlparse

from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

logger = logging.getLogger(__name__)


def _build_signed_string(
    signed_headers: str, method: str, path: str, headers: Any, body_digest: str
) -> str:
    out = []
    for signed_header in signed_headers.split(" "):
        if signed_header == "(request-target)":
            out.append("(request-target): " + method.lower() + " " + path)
        elif signed_header == "digest":
            out.append("digest: " + body_digest)
        else:
            out.append(signed_header + ": " + headers[signed_header])
    return "\n".join(out)


def _parse_sig_header(val: Optional[str]) -> Optional[Dict[str, str]]:
    if not val:
        return None
    out = {}
    for data in val.split(","):
        k, v = data.split("=", 1)
        out[k] = v[1 : len(v) - 1]  # noqa: black conflict
    return out


def _verify_h(signed_string, signature, pubkey):
    signer = PKCS1_v1_5.new(pubkey)
    digest = SHA256.new()
    digest.update(signed_string.encode("utf-8"))
    return signer.verify(digest, signature)


def _body_digest(body: str) -> str:
    h = hashlib.new("sha256")
    h.update(body)  # type: ignore
    return "SHA-256=" + base64.b64encode(h.digest()).decode("utf-8")


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
