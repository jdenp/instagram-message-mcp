from .client import DMMessage, InstagramClient
from .config import Config


class DMSender:
    """Sends a DM to every recipient listed in config."""

    def __init__(self, config: Config):
        self._config = config
        self._client = InstagramClient(config.sessionid)

    @property
    def aliases(self) -> dict[str, str]:
        """Return username -> alias mapping for agents."""
        return self._config.aliases

    def send_dm(self, recipient: str, message: str) -> bool:
        """Send message to a specific recipient. Returns True if successful."""
        # Resolve alias to username if needed
        username = self._config.aliases.get(recipient, recipient)
        user_id = self._client.get_user_id(username)
        self._client.send_dm(message, [user_id])
        print(f"Sent to {username}")
        return True

    def read_dm(self, recipient: str, max_messages: int = 10) -> dict[str, list[DMMessage]]:
        """Read last N messages from a specific recipient's thread."""
        # Resolve alias to username if needed
        username = self._config.aliases.get(recipient, recipient)
        return self._client.read_dms([username], max_messages)
