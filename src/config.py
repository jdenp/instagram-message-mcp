import json
import os


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""


class Config:
    """Loads and validates config.json and recipients.json."""

    def __init__(self, base_dir: str | None = None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self._config_path = os.path.join(self.base_dir, "config.json")
        self._recipients_path = os.path.join(self.base_dir, "recipients.json")
        self.sessionid: str | None = None
        self.username: str = ""
        self.message_text: str = "test"
        self.max_messages_per_thread: int = 10
        self.recipients: list[str] = []
        self._load()

    def _load(self) -> None:
        self._load_config()
        self._load_recipients()

    def _load_config(self) -> None:
        try:
            with open(self._config_path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ConfigError(f"Config file not found: {self._config_path}")
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config: {e}")

        self.sessionid = data.get("sessionid")
        if not self.sessionid:
            raise ConfigError("Missing 'sessionid' in config.json")

        self.username = data.get("username", "")
        self.message_text = data.get("message_text", "test")

        self.max_messages_per_thread = data.get("max_messages_per_thread", 10)
        if not isinstance(self.max_messages_per_thread, int) or self.max_messages_per_thread < 1:
            raise ConfigError("'max_messages_per_thread' must be a positive integer")

    def _load_recipients(self) -> None:
        try:
            with open(self._recipients_path, "r") as f:
                self.recipients = json.load(f)
        except FileNotFoundError:
            raise ConfigError(f"Recipients file not found: {self._recipients_path}")
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in recipients: {e}")

        if not isinstance(self.recipients, list):
            raise ConfigError("recipients.json must contain a JSON array")
        if not self.recipients:
            raise ConfigError("recipients.json is empty — add at least one username")
        for r in self.recipients:
            if not isinstance(r, str) or not r.strip():
                raise ConfigError(f"Invalid recipient entry: {r!r}")
