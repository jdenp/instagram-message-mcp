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

    @property
    def user_id(self) -> str:
        return self._client.user_id

    def get_user_id(self, username: str) -> str:
        """Resolve a username to its Instagram user ID."""
        return self._client.user_id_from_username(username)

    def send_dm(self, message: str, user_ids: list[str]) -> None:
        """Send a direct message to the given user IDs."""
        self._client.direct_send(message, user_ids=user_ids)

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
        try:
            user = self._client.user_info_by_id(user_id)
            return user.username
        except Exception:
            return f"user_{user_id}"
