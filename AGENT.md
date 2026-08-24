# Instagram Message MCP — Agent Guide

## Quick start

```powershell
cd C:\Repos\instagram-message-mcp
uv run python mcp_server.py
```

The server prints its own initialize response on startup, then reads JSON-RPC requests from stdin.

## Protocol

JSON-RPC 2.0 over stdin/stdout. Each request is a newline-delimited JSON object. The server auto-initializes — you only need to send `tools/call` requests after that.

### Sending a DM

```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"send_dm","arguments":{"recipient":"hyowon_hailey_","message":"I love you"}}}
```

### Reading DMs

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"read_dm","arguments":{"recipient":"huuuge_cak","max_messages":5}}}
```

### Listing recipients

```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"list_recipients"}}
```

## PowerShell gotcha

The `<` redirect operator is reserved in PowerShell. Use pipe instead:

```powershell
Get-Content requests.json | uv run python mcp_server.py
```

## Config

- `config/config.json` — Instagram session ID (required) and optional defaults
- `config/recipients.json` — Array of Instagram usernames you can message

## Tools

| Tool | Description |
|------|-------------|
| `send_dm(recipient, message)` | Send a DM to a recipient in recipients.json |
| `read_dm(recipient, max_messages=10)` | Read last N messages from a thread |
| `list_recipients()` | List configured recipients with aliases |