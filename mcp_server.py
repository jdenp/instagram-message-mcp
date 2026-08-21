#!/usr/bin/env python3
"""MCP server for Instagram DM operations."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config, ConfigError
from src.sender import DMSender


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
                "serverInfo": {"name": "instagram-mcp", "version": "1.0.0"},
            },
        }

    def handle_tools_list(self, params: dict, request_id: int) -> dict:
        """Handle MCP tools/list request."""
        tools = [
            {
                "name": "send_dm",
                "description": "Send a DM to all recipients in recipients.json",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message text to send (uses config message_text if omitted)",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "read_dms",
                "description": "Read last N messages from recipient threads",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "max_messages": {
                            "type": "integer",
                            "description": "Max messages per thread (uses config max_messages_per_thread if omitted)",
                        },
                    },
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
            elif tool_name == "read_dms":
                return self._handle_read_dms(arguments, request_id)
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
        message = args.get("message") or self.config.message_text
        sent = self.sender.send(message)
        result = f"Sent to {len(sent)} recipient(s): {', '.join(sent)}"
        return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": result}]}}

    def _handle_read_dms(self, args: dict, request_id: int) -> dict:
        """Handle read_dms tool call."""
        max_messages = args.get("max_messages") or self.config.max_messages_per_thread
        dms = self.sender.read_dms()
        formatted = _format_dms(dms)
        return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": formatted}]}}

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
