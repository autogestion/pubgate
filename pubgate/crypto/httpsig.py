"""

Mastodon instances won't accept requests that are not signed using this scheme.

"""
import base64
import hashlib
import logging
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional
from urllib.parse import urlsplit


from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

from pubgate.crypto.key import Key

logger = logging.getLogger(__name__)


def build_signing_string(headers, used_headers):
    return '\n'.join(map(lambda x: ': '.join([x.lower(), headers[x]]), used_headers))


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
        out[k] = v[1: len(v) - 1]  # noqa: black conflict
    return out


def _verify_h(signed_string, signature, pubkey):
    signer = PKCS1_v1_5.new(pubkey)
    digest = SHA256.new()
    digest.update(signed_string.encode("utf-8"))
    return signer.verify(digest, signature)


def verify(hsig, request, actor):
    k = Key(actor["id"])
    k.load_pub(actor["publicKey"]["publicKeyPem"])
    if k.key_id() != hsig["keyId"]:
        return False

    signed_string = _build_signed_string(
        hsig["headers"], request.method, request.path,
        request.headers, _body_digest(request.body)
    )
    return _verify_h(signed_string, base64.b64decode(hsig["signature"]), k.pubkey)


def _body_digest(body: str) -> str:
    h = hashlib.new("sha256")
    h.update(body)  # type: ignore
    return "SHA-256=" + base64.b64encode(h.digest()).decode("utf-8")


class HTTPSigAuth:
    """Requests auth plugin for signing requests on the fly."""

    def __init__(self, key, headers) -> None:
        self.key = key
        self.headers = headers

    def sign(self, url, body):
        headers = self.headers.copy()
        spl_url = urlsplit(url)

        bh = hashlib.new("sha256")
        try:
            body = body.encode("utf-8")
        except AttributeError:
            pass
        bh.update(body)
        
        headers.update({
            '(request-target)': f'post {spl_url.path}',
            "date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            'host': spl_url.netloc,
            'digest': "SHA-256=" + base64.b64encode(bh.digest()).decode("utf-8")
        })

        sigheaders = headers.keys()
        sigstring = build_signing_string(headers, sigheaders)

        signer = PKCS1_v1_5.new(self.key.privkey)
        digest = SHA256.new()
        digest.update(sigstring.encode("ascii"))
        sigdata = base64.b64encode(signer.sign(digest))

        sig = {
            'keyId': self.key.key_id(),
            'algorithm': 'rsa-sha256',
            'headers': ' '.join(sigheaders),
            'signature': sigdata.decode('ascii')
        }
        headers["signature"] = ','.join(['{}="{}"'.format(k, v) for k, v in sig.items()])

        return headers
