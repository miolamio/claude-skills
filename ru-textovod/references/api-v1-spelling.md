# API v1 — Spelling (Орфография)

## Endpoint

Single endpoint — returns results immediately (no polling required):

`POST https://textovod.com/api/spelling/user/add`

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

## Request

```bash
JSON_BODY=$(jq -n \
  --arg user_id "$TEXTOVOD_USER_ID" \
  --arg api_key "$TEXTOVOD_API_KEY" \
  --arg text "$TEXT" \
  '{user_id: $user_id, api_key: $api_key, text: $text, lang: "ru"}')

curl -s -X POST https://textovod.com/api/spelling/user/add \
  -H "Content-Type: application/json" \
  -d "$JSON_BODY"
```

## Response

Results come immediately in the response (status 1 = ready with results):

```json
{
  "status": 1,
  "result": "[{\"offset\":3,\"length\":7,\"mes\":\"Возможно найдена орфографическая ошибка.\",\"rep\":[\"прейдём\",\"придём\",\"пройдём\"]}]",
  "count": 1,
  "text": "Мы прийдём завтра на встречу чтобы обсудить новые предложения",
  "text_id": "f47705cdb11b54c7754ab4dc9359dea1"
}
```

**Important:** The `result` field is a **JSON-encoded string**, not a JSON object. Parse it with `fromjson`.

### Error object structure

Each error in the `result` array:

| Field | Type | Description |
|-------|------|-------------|
| `offset` | number | Character position in original text |
| `length` | number | Length of the problematic fragment |
| `mes` | string | Human-readable description of the error |
| `rep` | array | Suggested replacements (best first) |

## Parsing Results

```bash
# Parse the result string as JSON and format errors
echo "$RESPONSE" | jq -r '.result | fromjson | .[] | "«\(.mes)» offset:\(.offset) -> «\(.rep[0])»"'

# Get error count
echo "$RESPONSE" | jq '.count'

# Get original text
echo "$RESPONSE" | jq -r '.text'

# Extract just the word at offset+length from original text
# Use offset and length to slice from .text
```

### Building error descriptions

To show the actual misspelled word, extract it from the original text using `offset` and `length`:

```bash
echo "$RESPONSE" | jq -r '
  .text as $t |
  .result | fromjson | .[] |
  "«\($t[$offset:$offset+.length] // "?")» -> «\(.rep[0])» (\(.mes))"
'
```

Or simpler — slice the original text in bash:

```bash
ORIGINAL=$(echo "$RESPONSE" | jq -r '.text')
echo "$RESPONSE" | jq -r '.result | fromjson | .[] | "\(.offset) \(.length) \(.rep[0]) \(.mes)"' | while read off len rep mes; do
  word="${ORIGINAL:$off:$len}"
  echo "«$word» -> «$rep» ($mes)"
done
```

## Error Cases

- Missing `user_id` or `api_key` — returns auth error
- Text exceeds 100K chars — returns error before processing
- Empty text — returns error
- Status 30 — insufficient balance, prompt user to top up at textovod.com
