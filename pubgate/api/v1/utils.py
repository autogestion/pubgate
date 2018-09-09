import binascii
import os


def make_label(activity):
    label = activity["type"]
    if isinstance(activity["object"], dict):
        label = f'{label}: {activity["object"]["type"]}'
    return label


def random_object_id() -> str:
    """Generates a random object ID."""
    return binascii.hexlify(os.urandom(8)).decode("utf-8")
