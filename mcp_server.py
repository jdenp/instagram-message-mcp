#!/usr/bin/env python3
"""MCP server for Instagram DM operations."""

import json
import sys
from importlib.metadata import PackageNotFoundError, version as get_version
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config, ConfigError
from src.sender import DMSender


def _get_version() -> str:
    """Get package version from pyproject.toml metadata."""
    try:
        return get_version("instagram-message-mcp")
    except PackageNotFoundError:
        # Fallback: read from pyproject.toml directly
        pyproject = Path(__file__).parent / "pyproject.toml"
        for line in pyproject.read_text().splitlines():
            if line.startswith('version = '):
                return line.split('"')[1]
        return "0.0.0"


def _format_dms(dms: dict) -> str:
    """Format DMs into a readable string."""
    if not dms:
        return "No messages found from recipients."

    lines = []
    for username, messages in dms.items():
        lines.append(f"\n--- {username} ({len(messages)} message(s)) ---")
        for msg in messages:
            lines.append(f"  [{msg.timestamp}] {msg.text}")
    return "\n".join(lines)


class InstagramMCP:
    """MCP server for Instagram DM operations."""

    def __init__(self):
        self.config = Config()
        self.sender = DMSender(self.config)

    def handle_initialize(self, params: dict, request_id: int) -> dict:
        """Handle MCP initialize request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "instagram-mcp", "version": _get_version()},
            },
        }

    def handle_tools_list(self, params: dict, request_id: int) -> dict:
        """Handle MCP tools/list request."""
        tools = [
            {
                "name": "send_dm",
                "description": "Send a DM to a specific recipient",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": "Instagram username to send the DM to",
                        },
                        "message": {
                            "type": "string",
                            "description": "Message text to send (uses config message_text if omitted)",
                        },
                    },
                    "required": ["recipient"],
                },
            },
            {
                "name": "read_dm",
                "description": "Read last N messages from a specific recipient's thread",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": "Instagram username to read DMs from",
                        },
                        "max_messages": {
                            "type": "integer",
                            "description": "Max messages per thread (uses config max_messages_per_thread if omitted)",
                        },
                    },
                    "required": ["recipient"],
                },
            },
            {
                "name": "list_recipients",
                "description": "List all recipients with their aliases for agents to use",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        ]
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}



    def handle_tools_call(self, params: dict, request_id: int) -> dict:
        """Handle MCP tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "send_dm":
                return self._handle_send_dm(arguments, request_id)
            elif tool_name == "read_dm":
                return self._handle_read_dm(arguments, request_id)
            elif tool_name == "list_recipients":
                return self._handle_list_recipients(request_id)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}]},
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": str(e)},
            }

    def _handle_send_dm(self, args: dict, request_id: int) -> dict:
        """Handle send_dm tool call."""
        recipient = args.get("recipient")
        if not recipient:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": "Missing required field: recipient"}}
        message = args.get("message") or self.config.message_text
        success = self.sender.send_dm(recipient, message)
        result = f"Sent to {recipient}: {'ok' if success else 'failed'}"
        return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": result}]}}

    def _handle_read_dm(self, args: dict, request_id: int) -> dict:
        """Handle read_dm tool call."""
        recipient = args.get("recipient")
        if not recipient:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": "Missing required field: recipient"}}
        max_messages = args.get("max_messages") or self.config.max_messages_per_thread
        dms = self.sender.read_dm(recipient, max_messages)
        formatted = _format_dms(dms)
        return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": formatted}]}}

    def _handle_list_recipients(self, request_id: int) -> dict:
        """Handle list_recipients tool call."""
        aliases = self.sender.aliases
        if not aliases:
            result_text = "No recipients configured."
        else:
            lines = ["Recipients (username -> alias):"]
            for username, alias in aliases.items():
                lines.append(f"  {username} -> {alias}")
            result_text = "\n".join(lines)
        return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": result_text}]}}

    def process_request(self, request: dict) -> dict | None:
        """Process a JSON-RPC request and return response."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "initialize":
            return self.handle_initialize(params, request_id)
        elif method == "tools/list":
            return self.handle_tools_list(params, request_id)
        elif method == "tools/call":
            return self.handle_tools_call(params, request_id)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }


def main():
    """Main MCP server loop."""
    try:
        mcp = InstagramMCP()
    except ConfigError as e:
        error_msg = f"Config error: {e}"
        print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": error_msg}}), flush=True)
        sys.exit(1)

    # Send initialize response first
    init_response = mcp.handle_initialize({}, 0)
    print(json.dumps(init_response), flush=True)

    # Process requests from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = mcp.process_request(request)
            if response:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            continue


if __name__ == "__main__":
    main()
