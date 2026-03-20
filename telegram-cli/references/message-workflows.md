# Message Workflows

## Reading messages

### Chat history with time range

```bash
# Last 50 messages (default)
tg message history @channel

# Messages from a specific date range
tg message history @group --since 2026-03-01T00:00:00Z --until 2026-03-07T23:59:59Z

# Paginate through older messages
tg message history @chat --limit 100 --offset 100
```

### Forum topics

```bash
# List topics first
tg chat topics @supergroup

# Read messages in a specific topic
tg message history @supergroup --topic 42 --limit 20

# Send to a topic
tg message send @supergroup "Topic reply" --topic 42

# Search within a topic
tg message search --chat @supergroup --topic 42 --query "keyword"
```

### Get specific messages by ID

```bash
# Single message
tg message get @chat 1234

# Multiple messages (comma-separated, max 100)
tg message get @chat 1234,1235,1236

# Response includes a `notFound` array for missing IDs
```

### Pinned messages

```bash
tg message pinned @chat
tg message pinned @chat --limit 5
```

### Channel post replies/comments

```bash
# Get comments on channel post #42
tg message replies @channel 42

# Multiple posts
tg message replies @channel 42,43,44 --limit 20
```

## Searching

### Global search (all chats)

```bash
tg message search --query "meeting notes"
tg message search --query "budget" --limit 5
```

### Search in specific chat

```bash
tg message search --query "deadline" --chat @team_group
```

### Search by media type

```bash
tg message search --chat @group --filter photos
tg message search --chat @group --filter documents
tg message search --chat @group --filter urls
tg message search --chat @group --filter voice
```

All 17 filters: `photos`, `videos`, `photo_video`, `documents`, `urls`, `gifs`, `voice`, `music`, `round`, `round_voice`, `chat_photos`, `phone_calls`, `mentions`, `geo`, `contacts`, `pinned`

## Sending messages

### Basic send

```bash
tg message send @user "Hello!"
```

**Message length limit:** Telegram allows max 4096 characters per message. The CLI validates this and returns `MESSAGE_TOO_LONG` if exceeded. For longer content, split into multiple messages.

### Reply to a message

```bash
tg message send @chat "I agree!" --reply-to 1234
```

### Send from stdin (pipe content)

```bash
echo "Generated report summary" | tg message send @chat -
cat report.txt | tg message send @chat -
```

### Edit a sent message

```bash
tg message edit @chat 1234 "Updated text"

# Edit from stdin
echo "corrected text" | tg message edit @chat 1234 -
```

Note: Editing works within a 48-hour window for user messages. Same 4096-char limit applies.

### Forward messages

```bash
# Forward single message
tg message forward @source 1234 @destination

# Forward multiple
tg message forward @source 1234,1235,1236 @destination
```

## Reactions

```bash
# Add reaction
tg message react @chat 1234 👍

# Remove reaction
tg message react @chat 1234 👍 --remove
```

## Pinning

```bash
# Pin silently (default)
tg message pin @chat 1234

# Pin with notification
tg message pin @chat 1234 --notify

# Unpin
tg message unpin @chat 1234
```

## Deleting

Deletion requires an explicit scope flag:

```bash
# Delete for everyone (revoke)
tg message delete @chat 1234,1235 --revoke

# Delete for self only
tg message delete @chat 1234 --for-me
```

Max 100 message IDs per call.

## Polls

### Simple poll

```bash
tg message poll @chat --question "Where for lunch?" --option "Pizza" --option "Sushi" --option "Tacos"
```

### Quiz with correct answer

```bash
tg message poll @chat \
  --question "Capital of France?" \
  --option "London" \
  --option "Paris" \
  --option "Berlin" \
  --quiz --correct 1 \
  --solution "Paris has been the capital since the 10th century"
```

### Multiple choice, public votes, auto-close

```bash
tg message poll @chat \
  --question "Select all that apply" \
  --option "Option A" --option "Option B" --option "Option C" \
  --multiple --public --close-in 7200
```

`--close-in` is in seconds (7200 = 2 hours).
