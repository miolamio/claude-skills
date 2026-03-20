# API v1 — Punctuation (Пунктуация)

## Endpoints

- **Submit:** `POST https://textovod.com/api/punctuation/user/add`
- **Poll:** `POST https://textovod.com/api/punctuation/user/status`

## Authentication

Credentials passed in JSON body (not headers):

```json
{
  "user_id": "${TEXTOVOD_USER_ID}",
  "api_key": "${TEXTOVOD_API_KEY}",
  "text": "...",
  "lang": "ru"
}
```

## Limits

- Max text length: 100,000 characters
- Rate limit: 60 requests per minute

## Submit Request

```bash
JSON_BODY=$(jq -n \
  --arg user_id "$TEXTOVOD_USER_ID" \
  --arg api_key "$TEXTOVOD_API_KEY" \
  --arg text "$TEXT" \
  '{user_id: $user_id, api_key: $api_key, text: $text, lang: "ru"}')

curl -s -X POST https://textovod.com/api/punctuation/user/add \
  -H "Content-Type: application/json" \
  -d "$JSON_BODY"
```

### Submit Response

```json
{
  "status": 3,
  "text_id": "f47705cdb11b54c7754ab4dc9359dea1"
}
```

- `status: 3` — task queued
- `text_id` — use for polling

## Poll Request

Use `text_id` (not `id`) for polling:

```bash
POLL_BODY=$(jq -n \
  --arg user_id "$TEXTOVOD_USER_ID" \
  --arg api_key "$TEXTOVOD_API_KEY" \
  --arg text_id "$TEXT_ID" \
  '{user_id: $user_id, api_key: $api_key, text_id: $text_id}')

curl -s -X POST https://textovod.com/api/punctuation/user/status \
  -H "Content-Type: application/json" \
  -d "$POLL_BODY"
```

### Poll Response — Ready

```json
{
  "status": 2,
  "text_id": "f47705cdb11b54c7754ab4dc9359dea1",
  "punctuation": "<div>HTML formatted result with <mark> and <font> tags</div>",
  "result": {
    "punctuation": [
      {
        "paragraph": [
          {
            "offset": 27,
            "length": 1,
            "mes": "add",
            "rep": "."
          },
          {
            "offset": 29,
            "length": 5,
            "mes": "register",
            "rep": "Чтобы"
          },
          {
            "offset": 60,
            "length": 1,
            "mes": "add",
            "rep": "."
          }
        ]
      }
    ],
    "statistics": {
      "add": 2,
      "delete": 0,
      "register": 1,
      "ok": 0
    }
  },
  "text": "Мы прийдём завтра на встречу чтобы обсудить новые предложения",
  "resultText": [
    "Мы прийдём завтра на встречу чтобы обсудить новые предложения"
  ]
}
```

### Correction types (`mes` field)

| Type | Meaning |
|------|---------|
| `add` | Add punctuation mark (see `rep` for which) |
| `delete` | Remove punctuation mark |
| `register` | Change letter case (capitalize/lowercase) |
| `ok` | No change needed (informational) |

## Status Codes

| Code | Meaning |
|------|---------|
| 0 | Error / unknown |
| 1 | Processing |
| 2 | Ready (result available) |
| 3 | Queued |
| 30 | Insufficient balance |

## Parsing Results

```bash
# Get statistics
echo "$RESULT" | jq '.result.statistics'

# Get all corrections with details
echo "$RESULT" | jq -r '.result.punctuation[].paragraph[] | "\(.mes): offset \(.offset) -> «\(.rep)»"'

# Count total corrections
echo "$RESULT" | jq '[.result.punctuation[].paragraph[]] | length'

# Get original text
echo "$RESULT" | jq -r '.text'
```

### Building corrected text

The API returns corrections as offsets. To build the corrected text, apply corrections in reverse order (highest offset first) to avoid shifting positions:

```bash
# Get corrections sorted by offset descending
echo "$RESULT" | jq -r '[.result.punctuation[].paragraph[]] | sort_by(.offset) | reverse | .[] | "\(.offset) \(.length) \(.mes) \(.rep)"'
```

For simple cases, the `punctuation` HTML field contains an inline-rendered version.

## Error Cases

- Missing `user_id` or `api_key` — returns auth error
- Text exceeds 100K chars — returns error before processing
- Empty text — returns error
- Status 30 — insufficient balance, prompt user to top up at textovod.com
