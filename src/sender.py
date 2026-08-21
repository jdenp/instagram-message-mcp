from .client import DMMessage, InstagramClient
from .config import Config


class DMSender:
    """Sends a DM to every recipient listed in config."""

    def __init__(self, config: Config):
        self._config = config
        self._client = InstagramClient(config.sessionid)

    def send(self, message: str | None = None) -> list[str]:
        """Send message to all recipients. Returns list of usernames that succeeded."""
        text = message or self._config.message_text
        sent: list[str] = []
        for recipient in self._config.recipients:
            user_id = self._client.get_user_id(recipient)
            self._client.send_dm(text, [user_id])
            print(f"Sent to {recipient}")
            sent.append(recipient)
        return sent

    def read_dms(self) -> dict[str, list[DMMessage]]:
        """Read last N messages from threads involving recipients."""
        return self._client.read_dms(
            self._config.recipients,
            self._config.max_messages_per_thread,
        )
