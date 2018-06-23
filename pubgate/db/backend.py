import binascii
import os
import typing

import requests

from little_boxes.__version__ import __version__
from little_boxes.errors import ActivityNotFoundError
from little_boxes.errors import RemoteActivityGoneError
from little_boxes.urlutils import check_url, InvalidURLError

if typing.TYPE_CHECKING:
    from little_boxes import activitypub as ap  # noqa: type checking

from pubgate import version

class PGBackend:

    def user_agent(self) -> str:
        return (
            f"{requests.utils.default_user_agent()} (Pubgate/{version};"
            " +http://github.com/autogestion/pubgate)"
        )

    def random_object_id(self) -> str:
        """Generates a random object ID."""
        return binascii.hexlify(os.urandom(8)).decode("utf-8")

    def fetch_json(self, url: str, **kwargs):
        check_url(url)
        resp = requests.get(
            url,
            headers={"User-Agent": self.user_agent(), "Accept": "application/json"},
            **kwargs,
        )

        resp.raise_for_status()

        return resp

    def is_from_outbox(
        self, as_actor: "ap.Person", activity: "ap.BaseActivity"
    ) -> bool:
        return activity.get_actor().id == as_actor.id

    def fetch_iri(self, iri: str, **kwargs) -> "ap.ObjectType":  # pragma: no cover
        try:
            check_url(iri)
        # TODO for debug
        except InvalidURLError:
            pass

        # resp = requests.get(
        #     iri,
        #     headers={
        #         "User-Agent": self.user_agent(),
        #         "Accept": "application/activity+json",
        #     },
        #     **kwargs,
        # )

        # if resp.status_code == 404:
        #     raise ActivityNotFoundError(f"{iri} is not found")
        # elif resp.status_code == 410:
        #     raise RemoteActivityGoneError(f"{iri} is gone")
        #
        # resp.raise_for_status()

        return self.profile
