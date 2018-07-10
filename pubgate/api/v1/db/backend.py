import binascii
import os
import typing

import requests

from little_boxes.urlutils import check_url
from little_boxes.activitypub import _to_list

from pubgate.api.v1.db.models import Outbox


if typing.TYPE_CHECKING:
    from little_boxes import activitypub as ap  # noqa: type checking

from pubgate import version
import asyncio





async def fetch(session, url):
    print(url)
    async with session.get(url) as resp:
        resp = await resp.json()
    return resp


class NotBackend:

    def fetch_iri(self, iri: str, **kwargs) -> "ap.ObjectType":  # pragma: no cover

        check_url(iri, self.debug)
        # try:
        #     self.check_url(iri)
        # except URLLookupFailedError:
        #     # The IRI is inaccessible
        #     raise ActivityUnavailableError(f"unable to fetch {iri}, url lookup failed")
        #
        # try:
        #     resp = requests.get(
        #         iri,
        #         headers={
        #             "User-Agent": self.user_agent(),
        #             "Accept": "application/activity+json",
        #         },
        #         timeout=15,
        #         allow_redirects=False,
        #         **kwargs,
        #     )
        # except (
        #     requests.exceptions.ConnectTimeout,
        #     requests.exceptions.ReadTimeout,
        #     requests.exceptions.ConnectionError,
        # ):
        #     raise ActivityUnavailableError(f"unable to fetch {iri}, connection error")
        # if resp.status_code == 404:
        #     raise ActivityNotFoundError(f"{iri} is not found")
        # elif resp.status_code == 410:
        #     raise ActivityGoneError(f"{iri} is gone")
        # elif resp.status_code in [500, 502, 503]:
        #     raise ActivityUnavailableError(
        #         f"unable to fetch {iri}, server error ({resp.status_code})"
        #     )
        #
        # resp.raise_for_status()
        #
        # try:
        #     out = resp.json()
        # except json.JSONDecodeError:
        #     # TODO(tsileo): a special error type?
        #     raise ActivityUnavailableError(f"{iri} is not JSON")
        #
        # return out

        return self.profile

    def activity_url(self, obj_id):
        """URL for activity link."""
        return f"{self.base_url}/api/v1/outbox/{obj_id}"

    def note_url(self, obj_id):
        return self.activity_url(obj_id)

    def debug_mode(self) -> bool:
        """Should be overidded to return `True` in order to enable the debug mode."""
        return self.debug

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

    def post_to_remote_inbox(self, as_actor, payload: str, to: str) -> None:
        # tasks.post_to_inbox.delay(payload, to)
        pass

    def outbox_create(self, as_actor, create) -> None:
        self._handle_replies(as_actor, create)


class PGBackend(NotBackend):

    def outbox_new(self, as_actor, activity) -> None:
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(Outbox.insert_one(
             {
                "activity": activity.to_dict(),
                "type": _to_list(activity.type),
                "remote_id": activity.id,
                "meta": {"undo": False, "deleted": False},
             }), loop=loop)

    def _handle_replies(self, as_actor, create) -> None:
        """Go up to the root reply, store unknown replies in the `threads` DB and set the "meta.thread_root_parent"
        key to make it easy to query a whole thread."""
        in_reply_to = create.get_object().inReplyTo
        if not in_reply_to:
            return

        # new_threads = []
        # root_reply = in_reply_to
        # reply = ap.fetch_remote_activity(root_reply, expected=ap.ActivityType.NOTE)
        #
        # if not DB.inbox.find_one_and_update(
        #     {"activity.object.id": in_reply_to},
        #     {"$inc": {"meta.count_reply": 1, "meta.count_direct_reply": 1}},
        # ):
        #     if not DB.outbox.find_one_and_update(
        #         {"activity.object.id": in_reply_to},
        #         {"$inc": {"meta.count_reply": 1, "meta.count_direct_reply": 1}},
        #     ):
        #         # It means the activity is not in the inbox, and not in the outbox, we want to save it
        #         DB.threads.insert_one(
        #             {
        #                 "activity": reply.to_dict(),
        #                 "type": _to_list(reply.type),
        #                 "remote_id": reply.id,
        #                 "meta": {"undo": False, "deleted": False},
        #             }
        #         )
        #         new_threads.append(reply.id)
        #
        # while reply is not None:
        #     in_reply_to = reply.inReplyTo
        #     if not in_reply_to:
        #         break
        #     root_reply = in_reply_to
        #     reply = ap.fetch_remote_activity(root_reply, expected=ap.ActivityType.NOTE)
        #     q = {"activity.object.id": root_reply}
        #     if not DB.inbox.count(q) and not DB.outbox.count(q):
        #         DB.threads.insert_one(
        #             {
        #                 "activity": reply.to_dict(),
        #                 "type": _to_list(reply.type),
        #                 "remote_id": reply.id,
        #                 "meta": {"undo": False, "deleted": False},
        #             }
        #         )
        #         new_threads.append(reply.id)
        #
        # q = {"remote_id": create.id}
        # if not DB.inbox.find_one_and_update(
        #     q, {"$set": {"meta.thread_root_parent": root_reply}}
        # ):
        #     DB.outbox.update_one(q, {"$set": {"meta.thread_root_parent": root_reply}})
        #
        # DB.threads.update(
        #     {"remote_id": {"$in": new_threads}},
        #     {"$set": {"meta.thread_root_parent": root_reply}},
        # )

    async def build_ordered_collection(
        col, q=None, cursor=None, map_func=None, limit=50, col_name=None, first_page=False
    ):
        """Helper for building an OrderedCollection from a MongoDB query (with pagination support)."""
        col_name = col_name or col.name
        if q is None:
            q = {}

        if cursor:
            q["_id"] = {"$lt": ObjectId(cursor)}
        data = list(col.find(q, limit=limit).sort("_id", -1))

        if not data:
            return {
                "id": BASE_URL + "/" + col_name,
                "totalItems": 0,
                "type": ap.ActivityType.ORDERED_COLLECTION.value,
                "orederedItems": [],
            }

        start_cursor = str(data[0]["_id"])
        next_page_cursor = str(data[-1]["_id"])
        total_items = col.find(q).count()

        data = [_remove_id(doc) for doc in data]
        if map_func:
            data = [map_func(doc) for doc in data]

        # No cursor, this is the first page and we return an OrderedCollection
        if not cursor:
            resp = {
                "@context": ap.COLLECTION_CTX,
                "id": f"{BASE_URL}/{col_name}",
                "totalItems": total_items,
                "type": ap.ActivityType.ORDERED_COLLECTION.value,
                "first": {
                    "id": f"{BASE_URL}/{col_name}?cursor={start_cursor}",
                    "orderedItems": data,
                    "partOf": f"{BASE_URL}/{col_name}",
                    "totalItems": total_items,
                    "type": ap.ActivityType.ORDERED_COLLECTION_PAGE.value,
                },
            }

            if len(data) == limit:
                resp["first"]["next"] = (
                    BASE_URL + "/" + col_name + "?cursor=" + next_page_cursor
                )

            if first_page:
                return resp["first"]

            return resp

        # If there's a cursor, then we return an OrderedCollectionPage
        resp = {
            "@context": ap.COLLECTION_CTX,
            "type": ap.ActivityType.ORDERED_COLLECTION_PAGE.value,
            "id": BASE_URL + "/" + col_name + "?cursor=" + start_cursor,
            "totalItems": total_items,
            "partOf": BASE_URL + "/" + col_name,
            "orderedItems": data,
        }
        if len(data) == limit:
            resp["next"] = BASE_URL + "/" + col_name + "?cursor=" + next_page_cursor

        if first_page:
            return resp["first"]

        # XXX(tsileo): implements prev with prev=<first item cursor>?

        return resp


    # def add_extra_collection(raw_doc: Dict[str, Any]) -> Dict[str, Any]:
    #     if raw_doc["activity"]["type"] != ActivityType.CREATE.value:
    #         return raw_doc
    #
    #     raw_doc["activity"]["object"]["replies"] = embed_collection(
    #         raw_doc.get("meta", {}).get("count_direct_reply", 0),
    #         f'{raw_doc["remote_id"]}/replies',
    #     )
    #
    #     raw_doc["activity"]["object"]["likes"] = embed_collection(
    #         raw_doc.get("meta", {}).get("count_like", 0), f'{raw_doc["remote_id"]}/likes'
    #     )
    #
    #     raw_doc["activity"]["object"]["shares"] = embed_collection(
    #         raw_doc.get("meta", {}).get("count_boost", 0), f'{raw_doc["remote_id"]}/shares'
    #     )
    #
    #     return raw_doc
    #
    #
    # def activity_from_doc(raw_doc: Dict[str, Any], embed: bool = False) -> Dict[str, Any]:
    #     raw_doc = add_extra_collection(raw_doc)
    #     activity = clean_activity(raw_doc["activity"])
    #     return activity