import base64
import hashlib
import typing
from datetime import datetime
from typing import Any
from typing import Dict

from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from pyld import jsonld

if typing.TYPE_CHECKING:
    from .key import Key  # noqa: type checking


# cache the downloaded "schemas", otherwise the library is super slow
# (https://github.com/digitalbazaar/pyld/issues/70)
_CACHE: Dict[str, Any] = {}
LOADER = jsonld.requests_document_loader()


def _caching_document_loader(url: str) -> Any:
    if url in _CACHE:
        return _CACHE[url]
    resp = LOADER(url)
    _CACHE[url] = resp
    return resp


jsonld.set_document_loader(_caching_document_loader)


def _options_hash(doc):
    doc = dict(doc["signature"])
    for k in ["type", "id", "signatureValue"]:
        if k in doc:
            del doc[k]
    doc["@context"] = "https://w3id.org/identity/v1"
    normalized = jsonld.normalize(
        doc, {"algorithm": "URDNA2015", "format": "application/nquads"}
    )
    h = hashlib.new("sha256")
    h.update(normalized.encode("utf-8"))
    return h.hexdigest()


def _doc_hash(doc):
    doc = dict(doc)
    if "signature" in doc:
        del doc["signature"]
    normalized = jsonld.normalize(
        doc, {"algorithm": "URDNA2015", "format": "application/nquads"}
    )
    h = hashlib.new("sha256")
    h.update(normalized.encode("utf-8"))
    return h.hexdigest()


def verify_signature(doc, key: "Key"):
    to_be_signed = _options_hash(doc) + _doc_hash(doc)
    signature = doc["signature"]["signatureValue"]
    signer = PKCS1_v1_5.new(key.pubkey or key.privkey)
    digest = SHA256.new()
    digest.update(to_be_signed.encode("utf-8"))
    return signer.verify(digest, base64.b64decode(signature))


def generate_signature(doc, key: "Key"):
    options = {
        "type": "RsaSignature2017",
        "creator": doc["actor"] + "#main-key",
        "created": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
    }
    doc["signature"] = options
    to_be_signed = _options_hash(doc) + _doc_hash(doc)
    signer = PKCS1_v1_5.new(key.privkey)
    digest = SHA256.new()
    digest.update(to_be_signed.encode("utf-8"))
    sig = base64.b64encode(signer.sign(digest))
    options["signatureValue"] = sig.decode("utf-8")
