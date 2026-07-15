# Агенты в ResearchOS

ResearchOS рассчитан на выполнение исследовательских задач агентами разных
сред: Cursor, Codex, Claude и другими. Общие инструкции репозитория находятся в
[`AGENTS.md`](../AGENTS.md), а содержательные skills — в [`agents/skills/`](../agents/skills/).

## Где находится источник правды

| Сущность | Расположение |
|---|---|
| Дерево исследования и канбан | `koi-structure/project.md` проекта |
| Исследовательские выводы | `research.json` проекта |
| Публичные и рабочие отчёты | `reports/` проекта |
| Курируемые знания | `knowledge/*.md` проекта |
| Генерируемый индекс знаний | `KNOWLEDGE.md`, обновляет `koi/knowledge` |
| Содержательные agent skills | `agents/skills/` |

## Skills

- `koi-execute-card` — выполнить карточку эксперимента;
- `koi-report-review` — подготовить и проверить отчёт;
- `koi-done-research` — сформулировать вывод завершённого эксперимента;
- `koi-agent-chat` — ответить на вопрос из UI;
- `koi-knowledge-curator` — синтезировать накопленные знания;
- `koi-paper` и `koi-related-work` — подготовить материалы статьи;
- `koi-project-sync` — синхронизировать исследовательские проекты;
- `koi-prose-style` — проверить человекочитаемый текст.

Шаблоны и правила хранятся рядом с тем skill, который их применяет. Отдельного
глобального каталога стандартов нет.

## Cursor

`.cursor/hooks/` содержит только интеграционные hooks. Ссылки в
`.cursor/skills/` дают Cursor доступ к тем же общим skills без копирования.
Developer skills самого ResearchOS физически остаются в `.cursor/skills/`.

Подробнее: [исследовательский workflow](research-workflow.md),
[доменная модель](domain-model.md), [Inbox](agent-chat-inbox.md).
