# Agent Automation Patterns

Patterns for using `tg` in Claude Code agent workflows.

## Check auth before operations

Always verify authentication status before performing operations:

```bash
tg auth status
```

If not authenticated, inform the user they need to run `tg auth login` interactively.

## Efficient data reading

### Use --toon for large outputs

```bash
# Save tokens when reading history
tg message history @chat --toon --limit 50

# Save tokens when listing chats
tg chat list --toon
```

### Use --fields to narrow output

```bash
# Only get what you need
tg message history @chat --fields "id,text,date,senderId" --limit 20
tg chat list --fields "id,title,type,unreadCount"
```

### Combine for maximum efficiency

```bash
tg message history @chat --toon --fields "id,text,date" --limit 100
```

## Common agent workflows

### Summarize unread messages

```bash
# List chats with unread counts
tg chat list --fields "id,title,unreadCount" --toon

# Read unread messages from a specific chat
tg message history <chat_id> --limit <unread_count> --toon
```

### Find and respond to messages

```bash
# Search for messages mentioning a topic
tg message search --query "review needed" --chat @team --limit 10

# Reply to a specific message
tg message send @team "Reviewed and approved!" --reply-to <message_id>
```

### Monitor a channel

```bash
# Get latest messages
tg message history @channel --limit 5 --toon

# Get specific message details
tg message get @channel <id>
```

### Gather context about a chat

```bash
# Get chat metadata
tg chat info @group

# Get pinned messages (often contain rules/important info)
tg message pinned @group

# Get recent history
tg message history @group --limit 20 --toon
```

### Cross-chat operations

```bash
# Search globally
tg message search --query "quarterly report" --limit 5

# Forward found message to another chat
tg message forward @source <id> @destination
```

### Media workflow

```bash
# Find documents in a chat
tg message search --chat @group --filter documents --limit 5

# Download a specific document
tg media download @group <message_id> -o ./downloaded_file.pdf

# Send a file to someone
tg media send @user ./processed_file.pdf --caption "Here's the analysis"
```

## Error handling

The CLI returns structured JSON errors:

```json
{
  "ok": false,
  "error": { "code": "PEER_NOT_FOUND", "message": "..." }
}
```

Common error codes:
- `PEER_NOT_FOUND` - invalid chat identifier
- `MESSAGE_NOT_FOUND` - message ID doesn't exist
- `CHAT_WRITE_FORBIDDEN` - no permission to write
- `CHAT_ADMIN_REQUIRED` - admin privileges required (e.g., listing members)
- `MESSAGE_TOO_LONG` - message exceeds 4096-char limit
- `UNKNOWN_INVITE_TYPE` - unrecognized invite link result
- `USER_BLOCKED` - user has blocked you
- `FLOOD_WAIT_X` - rate limited (wait X seconds)
- `AUTH_KEY_UNREGISTERED` - session expired, re-login needed

## Rate limiting

Telegram enforces rate limits. For bulk operations:
- Don't send messages in rapid succession
- Space out search queries
- Use batch operations where available (e.g., `tg message get` with multiple IDs)

## Stdin piping for dynamic content

Generate content and send it directly:

```bash
echo "Generated summary: ..." | tg message send @chat -
```

This is useful when Claude generates text that should be sent as a message.
