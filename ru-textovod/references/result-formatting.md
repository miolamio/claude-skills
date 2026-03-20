# Result Formatting

## Two Output Modes

### Detailed Mode (default)

Use for spelling and punctuation checks, and when user wants to see errors.

```
### Найденные ошибки (N)

1. «неправильнoe» -> «правильное» (орфография)
2. «предложение без запятой» -> «предложение, с запятой» (пунктуация)

### Исправленный текст

[corrected text]
```

For autocorrection in detailed mode, show a diff-style comparison:

```
### Автокоррекция

**Изменения:**

1. «прийдём» -> «придём» (грамматика)
2. «чтобы» -> «, чтобы» (пунктуация)

### Исправленный текст

[corrected text]
```

To generate the diff, compare original text with corrected text word by word.

### Quick Mode

Triggered by: «просто исправь», «без деталей», «только текст», «quick»

```
Исправлено ошибок: N

[corrected text]
```

If no errors found:

```
Ошибок не найдено. Текст корректен.
```

## Formatting Rules

- Use Russian quotation marks «ёлочки» for quoted words
- Use `->` arrow between original and corrected
- Group errors by type if mixed (орфография, пунктуация, грамматика)
- Show error count in heading
- Put corrected text in a clean block without extra formatting
- If text is short (< 3 sentences), show inline. If long, use a fenced block.

## Combined Check Results

When user requests multiple checks (e.g., spelling + punctuation):

```
### Орфография (N ошибок)

1. «слово» -> «слово» (орфография)

### Пунктуация (M ошибок)

1. «фраза» -> «фраза» (пунктуация)

### Исправленный текст

[text with all corrections applied]
```
