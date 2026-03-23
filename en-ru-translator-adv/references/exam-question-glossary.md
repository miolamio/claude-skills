# Exam Question Translation Glossary (Claude / AI / Architecture)

Domain-specific terminology for translating certification exam questions about Claude, LLM APIs, and agentic architecture.

## Terms That Stay in English

| English | Notes |
|---------|-------|
| API, SDK, REST, HTTP, JSON, XML, YAML, CSV | Abbreviations and formats |
| enum, string, boolean, integer, float, null | Data types |
| hook, callback, middleware, endpoint | Architecture patterns (hook = хук in text) |
| tool, tool use, tool call | Claude API context |
| system prompt, user prompt | LLM context |
| token, context window | LLM context |
| few-shot, zero-shot, chain-of-thought | Prompting techniques |
| RAG, streaming, batch, MCP | |
| scratchpad | As part of compound: scratchpad-файл |

## Terms That Must Be Translated

| English | Russian | DO NOT use |
|---------|---------|------------|
| extraction schema | extraction-схема | «схема извлечения» (без «данных») |
| severity | severity (code), уровень критичности (text) | «серьёзность» |
| companion field | сопутствующее поле | «поле-компаньон», «отдельное поле» |
| correct answer | правильный ответ | «корректный ответ» |
| explanation | комментарий, пояснение | «экспланация» |
| deterministic | детерминированный | «детерминистский» |
| probabilistic | вероятностный | «пробабилистический» |
| enforcement | обеспечение соблюдения, контроль соблюдения | «энфорсмент», «принуждение» |
| human escalation | эскалация на оператора | «передача человеку», «перенаправление к человеку» |
| refund | возврат средств | «рефанд», «возврат» (без «средств» — двусмысленно) |
| validation | валидация | «проверка» (слишком общее) |
| classification | классификация | «ярлык», «категоризация» |
| agentic | агентный | «агентический», «агентивный» |
| workflow | рабочий процесс | «воркфлоу» |
| option / variant (test) | вариант ответа | «опция» |
| prerequisite (programmatic) | предусловие | «предпосылка» |

## Context-Dependent Terms

| English | Context → Russian |
|---------|-------------------|
| issue | bug tracker → «задача»; audit → «замечание»; general → «проблема» |
| process | verb → «обрабатывать»; noun → «процесс» |
| handle | «обрабатывать» (requests), «поддерживать» (formats) |
| implement | «реализовать» (function), «внедрить» (solution) |
| misuse | «использовать не по назначению» (NOT «злоупотреблять» — too intentional) |

## Context-Sensitive Terms

| English | DevOps/CI context | Data processing context |
|---------|-------------------|------------------------|
| pipeline | CI/CD-пайплайн, пайплайн | конвейер |

| English | Claude/LLM context | General |
|---------|-------------------|---------|
| conversation/session | диалог, контекст | NOT «разговор» |

| English | Russian | Do NOT use |
|---------|---------|------------|
| overhead | накладные расходы | «оверхед» |
| burden | нагрузка | «бремя» (too literary) |
| safely (code) | безопасно, без побочных эффектов | «в безопасности» |

## Exam Question Structure

| EN field | RU field |
|----------|----------|
| Question | Вопрос |
| Options | Варианты |
| Correct Answer | Правильный ответ |
| Explanation | Комментарий |
| Source | Источник |
| Section | Раздел |
| Scenario | Сценарий |
