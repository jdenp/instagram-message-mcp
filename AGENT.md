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

**Important:** `read_dm` expects the Instagram **username** (e.g. `huuuge_cak`), not the alias (e.g. `laurence`). Threads are matched by Instagram username, so passing an alias will fail to find the correct thread. Use `list_recipients` to see which entries are usernames vs aliases.

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

## Notes

- `read_dm` returns at most 10 messages by default. You can read up to 20, but reading 50 or more may timeout.
- Reels aren't shown in DM threads — they appear as reactions but not as full messages. When reading responses, only consider actual text messages.

## Correct usage patterns

### Sending a non-ASCII DM

```python
import json
cfg = json.load(open('config/config.json'))
from src.client import InstagramClient
c = InstagramClient(cfg['sessionid'])
uid = c.get_user_id('huuuge_cak')
c.send_dm('더러운 터키놈 자비스의 선물입니다', [uid])
```

`_send_dm_raw` uses `private_request` with `with_signature=False`, which handles UTF-8 correctly.

### Reading a thread and filtering by sender

```python
jdenp_id = int(c.user_id)
threads = c._client.direct_threads()
for t in threads:
    for u in t.users:
        if u.username == 'huuuge_cak':
            msgs = c._client.direct_messages(t.pk, amount=20)
            for m in msgs:
                sender_id = m.user_id
                if sender_id == jdenp_id:
                    name = 'you'
                else:
                    try:
                        name = c._resolve_username(sender_id)
                    except:
                        name = str(sender_id)
                print(f'{m.timestamp} | {name}: {repr(m.text)}')
```

### Using the MCP tools directly

```python
result = c.read_dms(['huuuge_cak'], 10)
for user, msgs in result.items():
    for m in msgs:
        print(f'{m.timestamp} | {user}: {m.text}')
```
