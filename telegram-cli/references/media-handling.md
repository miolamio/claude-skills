# Media Handling

## Downloading media

### Download from a specific message

```bash
# Download to current directory (auto-named)
tg media download @channel 42

# Download to specific path
tg media download @channel 42 -o ./photo.jpg

# Download from multiple messages
tg media download @channel 42,43,44
```

### Find media first, then download

```bash
# Find photos in a chat
tg message search --chat @channel --filter photos --limit 5

# Find documents
tg message search --chat @group --filter documents --limit 10

# Then download by message ID
tg media download @channel <id>
```

## Uploading and sending media

### Single file

```bash
tg media send @chat ./photo.jpg
tg media send @chat ./document.pdf
```

### Album (multiple files)

When sending multiple files, they are grouped as an album:

```bash
tg media send @chat ./img1.jpg ./img2.jpg ./img3.jpg
```

### With caption

```bash
tg media send @chat ./report.pdf --caption "Q1 Financial Report"
```

### Reply with media

```bash
tg media send @chat ./screenshot.png --reply-to 1234
```

### Send to forum topic

```bash
tg media send @supergroup ./file.pdf --topic 42
```

## Supported media types

The CLI handles all Telegram media types:
- Photos (JPEG, PNG, etc.)
- Videos (MP4, etc.)
- Documents (any file type)
- Voice messages
- Audio files
- Stickers
- Video messages (round)

The media type is determined automatically by Telegram based on the file.
