# Instagram DM MCP Server

MCP (Model Context Protocol) server for sending and reading Instagram DMs.

## Quick Start

```bash
uv run mcp_server.py
```

The server communicates via JSON-RPC 2.0 over stdin/stdout.

## Setup

1. Copy `config/config.json.template` to `config/config.json` - add your `sessionid`, optional `username`, and `max_messages_per_thread`.
2. Copy `config/recipients.json.template` to `config/recipients.json` - list of Instagram usernames with optional aliases.
3. The `.json` files are gitignored; the `.template` files are tracked as guides.

## Tools

### send_dm(message="test")

Send a DM to all recipients in `recipients.json`.

**Parameters:**

- `message` (optional) - Message text to send (uses `message_text` from config if omitted)

### read_dm(recipient, max_messages=10)

Read the last N messages from a specific recipient's thread.

**Parameters:**

- `recipient` (required) - Instagram username to read DMs from
- `max_messages` (optional) - Max messages per thread (uses `max_messages_per_thread` from config if omitted)

### list_recipients()

List all configured recipients with their aliases. Agents should use this tool to discover who they can message.

**Parameters:** None

## Config

| Field | Default | Description |
|---|---|---|
| `sessionid` | *(required)* | Your Instagram session ID |
| `username` | `""` | Your Instagram username (optional) |
| `message_text` | `"test"` | Message sent when using send_dm |
| `max_messages_per_thread` | `10` | Max messages to read per thread |

**ONLY** send to recipients in `recipients.json`. Do not modify the script directly.

## Recipient Aliases

In `recipients.json`, each entry can include an `alias` field for agents to use:

```json
[
    {
        "username": "john_doe",
        "alias": "John Doe"
    }
]
```

The alias is optional - if omitted, the username is used. Use the `list_recipients` tool to see all configured aliases. Plain string entries (backwards compat) are also supported:

```json
["john_doe", "jane_smith"]
```
