---
name: ru-textovod
description: >
  Checks Russian text for spelling, punctuation, and grammar via Textovod.com API.
  Use when user says "проверь текст", "проверь орфографию", "проверь пунктуацию",
  "автокоррекция", "исправь ошибки", "/ru-textovod", or after writing/editing
  Russian text. Three independent commands: autocorrection (default), spelling,
  punctuation. NOT for stylistic editing (use ru-editor).
metadata:
  author: Anthony Vdovitchenko @ Automatica (https://t.me/aiwizards)
  version: 1.0.0
  category: proofreading
allowed-tools: Bash(curl:*) Bash(jq:*) Bash(echo:*)
---

# Russian Text Proofreader (Проверка русского текста)

## Important Rules

- **Default command is autocorrection** (API v2 grammar). Use it unless the user explicitly asks for spelling or punctuation separately.
- **Never modify files without user permission.** Show the corrected text and ask before applying changes.
- **This skill is for proofreading — spelling, punctuation, grammar.** For stylistic editing (AI markers, informational style, voice), recommend `ru-editor`.
- Always use `jq -n --arg` to build JSON bodies — never interpolate text directly into JSON strings.
- Always escape and validate text before sending to API.

## Prerequisites — API Key Setup

Three environment variables are required:

| Variable | API | Purpose |
|----------|-----|---------|
| `TEXTOVOD_USER_ID` | v1 | User ID for spelling/punctuation |
| `TEXTOVOD_API_KEY` | v1 | API key for spelling/punctuation |
| `TEXTOVOD_API2_TOKEN` | v2 | Bearer token for autocorrection |

### Check Credentials

Before any API call, check that the required env vars are set:

```bash
# For autocorrection (API v2)
echo "${TEXTOVOD_API2_TOKEN:+set}"

# For spelling/punctuation (API v1)
echo "${TEXTOVOD_USER_ID:+set} ${TEXTOVOD_API_KEY:+set}"
```

### If Credentials Are Missing

Tell the user which variables are missing and how to set them:

```
Для работы нужны API-ключи Textovod.com.

Получите ключи на https://textovod.com/api и добавьте в ~/.zshrc:

export TEXTOVOD_USER_ID="your_user_id"
export TEXTOVOD_API_KEY="your_api_key"
export TEXTOVOD_API2_TOKEN="your_api2_token"

Затем перезапустите терминал или выполните: source ~/.zshrc
```

Alternatively, keys can be set in Claude Code settings (`~/.claude/settings.json`) under `env`.

## Three Commands

### 1. Autocorrection (default)

**Trigger:** «проверь текст», «автокоррекция», «исправь ошибки», or no specific command.

Neural network-based. Fixes grammar, spelling, and punctuation in one pass. Best for general proofreading.

- **API:** v2 grammar
- **Requires:** `TEXTOVOD_API2_TOKEN`
- **Max:** 35,000 characters
- **Reference:** [references/api-v2-grammar.md](references/api-v2-grammar.md)

### 2. Spelling

**Trigger:** «проверь орфографию», «spelling», «орфография».

Dictionary-based spelling check. Returns individual misspelled words with suggestions.

- **API:** v1 spelling
- **Requires:** `TEXTOVOD_USER_ID` + `TEXTOVOD_API_KEY`
- **Max:** 100,000 characters
- **Reference:** [references/api-v1-spelling.md](references/api-v1-spelling.md)

### 3. Punctuation

**Trigger:** «проверь пунктуацию», «punctuation», «пунктуация», «запятые».

Rule-based punctuation check. Returns corrected text with punctuation fixes.

- **API:** v1 punctuation
- **Requires:** `TEXTOVOD_USER_ID` + `TEXTOVOD_API_KEY`
- **Max:** 100,000 characters
- **Reference:** [references/api-v1-punctuation.md](references/api-v1-punctuation.md)

## Input Handling

### Inline Text (primary)

User provides text directly in the message. Extract the text to check.

### File Path

User provides a file path. Read the file content, then proceed as with inline text.

```bash
TEXT=$(cat "/path/to/file.txt")
```

### JSON Escaping

**Always** use `jq -n --arg` to safely embed text into JSON:

```bash
JSON_BODY=$(jq -n --arg text "$TEXT" '{text: $text, lang: "ru"}')
```

Never do `{"text": "$TEXT"}` — this breaks on quotes, newlines, and special characters.

### Character Limit Check

Before sending, verify text length:

```bash
CHAR_COUNT=$(echo -n "$TEXT" | wc -c)
# API v2: max 35000
# API v1: max 100000
```

If text exceeds the limit, inform the user and suggest splitting.

## API Workflow

Each API has a different workflow:

### Spelling (v1) — Immediate Response

Returns results in the submit response. No polling needed.

```bash
JSON_BODY=$(jq -n \
  --arg user_id "$TEXTOVOD_USER_ID" \
  --arg api_key "$TEXTOVOD_API_KEY" \
  --arg text "$TEXT" \
  '{user_id: $user_id, api_key: $api_key, text: $text, lang: "ru"}')

RESPONSE=$(curl -s -X POST https://textovod.com/api/spelling/user/add \
  -H "Content-Type: application/json" \
  -d "$JSON_BODY")

# result is a JSON string — parse with fromjson
echo "$RESPONSE" | jq -r '.result | fromjson | .[] | "\(.offset) \(.length) \(.mes) \(.rep[0])"'
```

### Punctuation (v1) — Submit + Poll with `text_id`

```bash
# Submit
RESPONSE=$(curl -s -X POST https://textovod.com/api/punctuation/user/add \
  -H "Content-Type: application/json" -d "$JSON_BODY")
TEXT_ID=$(echo "$RESPONSE" | jq -r '.text_id')

# Poll (separate Bash calls, 3 sec apart, use text_id not id)
POLL_BODY=$(jq -n \
  --arg user_id "$TEXTOVOD_USER_ID" \
  --arg api_key "$TEXTOVOD_API_KEY" \
  --arg text_id "$TEXT_ID" \
  '{user_id: $user_id, api_key: $api_key, text_id: $text_id}')
RESULT=$(curl -s -X POST https://textovod.com/api/punctuation/user/status \
  -H "Content-Type: application/json" -d "$POLL_BODY")
# status 2 = ready
```

### Autocorrection (v2) — Submit + Poll

**Important:** Do NOT send `id` in the request body — the API generates its own UUID.

```bash
# Submit (no id field!)
JSON_BODY=$(jq -n --arg text "$TEXT" '{text: $text, lang: "ru"}')
RESPONSE=$(curl -s -X POST https://textovod.com/api/v2/text/grammar \
  -H "Authorization: Bearer ${TEXTOVOD_API2_TOKEN}" \
  -H "Content-Type: application/json" -d "$JSON_BODY")
TASK_ID=$(echo "$RESPONSE" | jq -r '.id')

# Poll (separate Bash calls, 3 sec apart)
POLL_BODY=$(jq -n --arg id "$TASK_ID" '{id: $id}')
RESULT=$(curl -s -X POST https://textovod.com/api/v2/text/grammar/result \
  -H "Authorization: Bearer ${TEXTOVOD_API2_TOKEN}" \
  -H "Content-Type: application/json" -d "$POLL_BODY")
# Corrected text: jq -r '.messages[] | select(.role == "assistant") | .content'
```

**Polling:** Make each poll as a separate Bash tool call with `sleep 3` at the start. Max 15 attempts.

## Output Modes

See [references/result-formatting.md](references/result-formatting.md) for full formatting details.

### Detailed Mode (default)

Show list of errors + corrected text:

```
### Найденные ошибки (N)

1. «неправильнoe» -> «правильное» (орфография)
2. «предложение без запятой» -> «предложение, с запятой» (пунктуация)

### Исправленный текст

[corrected text]
```

### Quick Mode

Triggered by: «просто исправь», «без деталей», «только текст»

```
Исправлено ошибок: N

[corrected text]
```

## Error Handling

| Error | Action |
|-------|--------|
| Missing API keys | Show setup instructions (see Prerequisites) |
| Status 30 (insufficient balance) | Tell user: «Недостаточно средств на балансе Textovod. Пополните на https://textovod.com» |
| Timeout (15 polls without result) | Tell user: «Сервис не ответил за 45 секунд. Попробуйте позже или с текстом покороче.» |
| Rate limit (429) | Wait 5 seconds, retry once |
| Text too long | Show limit and suggest splitting |
| Empty text | Tell user: «Нет текста для проверки.» |
| Network error | Show error and suggest retrying |

## Integration with Other Skills

- **After checking** — if text has stylistic issues (AI markers, bureaucratese, weak verbs), suggest: «Текст грамматически верен. Хотите стилистическую редактуру? Используйте `ru-editor`.»
- **After `ru-editor`** — suggest: «Хотите проверить орфографию и пунктуацию? Используйте `ru-textovod`.»
- **After `en-ru-translator-adv`** — suggest proofreading the translation with `ru-textovod`.
