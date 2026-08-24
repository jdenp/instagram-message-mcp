from dataclasses import dataclass

from instagrapi import Client


@dataclass
class DMMessage:
    username: str
    timestamp: str
    text: str


class InstagramClient:
    """Thin wrapper around instagrapi.Client for login and DM operations."""

    def __init__(self, sessionid: str):
        self._client = Client()
        self._client.login_by_sessionid(sessionid)
        self._username_cache: dict[int, str] = {}

    @property
    def user_id(self) -> str:
        return self._client.user_id

    def get_user_id(self, username: str) -> str:
        """Resolve a username to its Instagram user ID."""
        return self._client.user_id_from_username(username)

    def send_dm(self, message: str, user_ids: list[str]) -> None:
        """Send a direct message to the given user IDs."""
        self._send_dm_raw(message, user_ids)

    def _send_dm_raw(self, message: str, user_ids: list[str]) -> None:
        """Send DM via instagrapi's private_request (same path as direct_send)."""
        import json as json_mod
        import uuid as uuid_mod

        client = self._client
        token = str(uuid_mod.uuid4())

        kwargs = {
            "action": "send_item",
            "is_x_transport_forward": "false",
            "send_silently": "false",
            "is_shh_mode": "0",
            "send_attribution": "message_button",
            "client_context": token,
            "device_id": client.android_device_id,
            "mutation_token": token,
            "_uuid": str(client.uuid),
            "btt_dual_send": "false",
            "nav_chain": "1qT:feed_timeline:1,1qT:feed_timeline:2,1qT:feed_timeline:3,7Az:direct_inbox:4,7Az:direct_inbox:5,5rG:direct_thread:7",
            "is_ae_dual_send": "false",
            "offline_threading_id": token,
            "text": message,
            "recipient_users": json_mod.dumps([[int(uid) for uid in user_ids]]),
        }

        result = client.private_request(
            "direct_v2/threads/broadcast/text/",
            data=client.with_default_data(kwargs),
            with_signature=False,
        )
        if result.get("status") != "ok":
            print(f"DM raw send error: {result}")

    def read_dms(
        self,
        recipients: list[str],
        max_per_thread: int,
    ) -> dict[str, list[DMMessage]]:
        """Read last N messages from threads involving the given recipients.

        Returns a dict mapping username -> list of DMMessage.
        Only includes threads where at least one participant matches a recipient.
        """
        recipient_set = set(recipients)
        result: dict[str, list[DMMessage]] = {}

        # Fetch all threads from inbox
        threads = self._client.direct_threads()

        for thread in threads:
            # Check if any participant is a recipient
            thread_users = {u.username for u in thread.users}
            matching_users = thread_users & recipient_set
            if not matching_users:
                continue

            # Fetch messages from this thread
            messages = self._client.direct_messages(thread.pk, amount=max_per_thread)

            for msg in messages:
                sender_username = self._resolve_username(msg.user_id)
                if sender_username in matching_users:
                    if sender_username not in result:
                        result[sender_username] = []
                    result[sender_username].append(
                        DMMessage(
                            username=sender_username,
                            timestamp=str(msg.timestamp),
                            text=msg.text or "",
                        )
                    )

        return result

    def _resolve_username(self, user_id: int) -> str:
        """Resolve a user ID to a username (cached)."""
        if user_id in self._username_cache:
            return self._username_cache[user_id]
        try:
            name = self._client.username_from_user_id(user_id)
            self._username_cache[user_id] = name
            return name
        except Exception:
            fallback = f"user_{user_id}"
            self._username_cache[user_id] = fallback
            return fallback
