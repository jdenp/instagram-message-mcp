# Instagram DM MCP Server

MCP (Model Context Protocol) server for sending and reading Instagram DMs.

## Quick Start

```bash
uv run mcp_server.py
```

The server communicates via JSON-RPC 2.0 over stdin/stdout.

## Setup

1. Edit `config.json` - add your `sessionid`, optional `username`, and `max_messages_per_thread`.
2. Edit `recipients.json` - list of Instagram usernames to send to or read from.

## Tools

### send_dm

Send a DM to all recipients in `recipients.json`.

**Parameters:**

- `message` (optional) - Message text to send (uses `message_text` from config if omitted)

### read_dms

Read the last N messages from recipient threads.

**Parameters:**

- `max_messages` (optional) - Max messages per thread (uses `max_messages_per_thread` from config if omitted)

## Config

| Field | Default | Description |
|---|---|---|
| `sessionid` | *(required)* | Your Instagram session ID |
| `username` | `""` | Your Instagram username (optional) |
| `message_text` | `"test"` | Message sent when using send_dm |
| `max_messages_per_thread` | `10` | Max messages to read per thread |

**ONLY** send to recipients in `recipients.json`. Do not modify the script directly.
