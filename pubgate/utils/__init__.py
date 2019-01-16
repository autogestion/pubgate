import binascii
import os
from typing import Any
from typing import List
from typing import Union
from html.parser import HTMLParser


def make_label(activity):
    label = activity["type"]
    if isinstance(activity.get("object", None), dict):
        label = f'{label}: {activity["object"]["type"]}'
    return label


def random_object_id() -> str:
    """Generates a random object ID."""
    return binascii.hexlify(os.urandom(8)).decode("utf-8")


def _to_list(data: Union[List[Any], Any]) -> List[Any]:
    """Helper to convert fields that can be either an object or a list of objects to a
    list of object."""
    if isinstance(data, list):
        return data
    return [data]


def reply_origin(obj, uri):
    reply = obj.get("inReplyTo", None)
    return reply.startswith(uri) if reply else False


def check_origin(obj, uri):
    if isinstance(obj, str):
        return obj.startswith(uri)
    elif isinstance(obj, dict):
        return reply_origin(obj, uri)


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
