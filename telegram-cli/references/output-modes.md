# Output Modes & Field Selection

## JSON (default)

All responses wrapped in a standard envelope:

```bash
tg chat list --limit 2
```

```json
{
  "ok": true,
  "data": [
    { "id": "123", "title": "Group Name", "type": "supergroup" },
    { "id": "456", "title": "Channel", "type": "channel" }
  ]
}
```

Errors return:

```json
{
  "ok": false,
  "error": { "code": "PEER_NOT_FOUND", "message": "Could not resolve..." }
}
```

## Human-readable

Formatted for terminal display:

```bash
tg chat info @channel --human
```

```
Chat: Tech News
ID: -1001234567890
Username: @technews
Type: channel
Members: 12,345
Description: Latest tech updates
```

## JSONL (streaming)

One JSON object per line, no envelope. Best for list commands and piping:

```bash
tg chat list --jsonl --limit 3
```

```
{"id":"123","title":"Group","type":"supergroup"}
{"id":"456","title":"Channel","type":"channel"}
{"id":"789","title":"User","type":"user"}
```

## TOON (token-efficient)

Optimized for LLM consumption, 31-40% token savings on typical Telegram data:

```bash
tg message history @chat --toon --limit 5
```

**Use `--toon` when:** reading large histories, searching across chats, or any command that returns substantial data. Significantly reduces context window usage.

## Field selection

Narrow output to specific fields using `--fields`:

```bash
# Only get id and title from chat list
tg chat list --fields "id,title" --limit 5

# Nested field access with dot notation
tg message history @chat --fields "id,text,date,sender.id,sender.username" --limit 10

# Combine with TOON for maximum efficiency
tg message history @chat --fields "id,text,date" --toon --limit 50
```

## Choosing the right mode

| Scenario | Recommended |
|----------|-------------|
| Agent reading messages | `--toon` or `--fields` to save tokens |
| Agent parsing data | `--json` (default) for structured access |
| Streaming large lists | `--jsonl` for line-by-line processing |
| Showing to user | `--human` for readability |
| Minimal data needed | `--fields "field1,field2"` |
| Large history analysis | `--toon --fields "id,text,date"` |
