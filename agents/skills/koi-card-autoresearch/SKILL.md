---
name: koi-card-autoresearch
description: >-
  Orchestrate a long-running ResearchOS kanban experiment with three agent
  roles (Manager, Researcher, Debugger): start the card, run/monitor the job,
  triage failures, keep report §3 and kanban in sync via koi-execute-card.
  TRIGGER when the user says «проведи системное исследование по карточке»,
  «автоисследование», «card-autoresearch», or asks for manager/researcher/
  debugger cadence on a card — not for short one-shot runs (use koi-execute-card).
---

# KOI: автоисследование по карточке

Долгий прогон **одной** карточки канбана с разделением ролей. Базовый
**koi-execute-card** остаётся законом для канбана, §3 и отчёта; этот скилл
добавляет оркестрацию: кто стартует, кто крутит job и смотрит пульс, кто
только диагностирует сбои.

Короткий локальный эксперимент «сделай и закрой» → **koi-execute-card**.
Многочасовой / remote / нужен дебаггер по расписанию → **koi-card-autoresearch**.

## Чем отличается от koi-execute-card

| | koi-execute-card | koi-card-autoresearch |
|--|------------------|------------------------|
| Владение | один агент делает всё сразу | три роли с разным правом писать |
| Длина | минуты–часы в одной сессии | часы–сутки, watch/debug loops |
| Сбои | чинит тот же агент | Дебаггер только рекомендует; чинит Исследователь |
| Специфика запуска | любая | подключает **project-specific** скрипты/скилл, если есть |

Пример project-specific реализации протокола: `verl-experiment-run` (CrafText /
verl на remote). В каталоге ResearchOS скриптов GPU нет — только роли и cadence.

## Триггер

> **«Проведи системное исследование по карточке …»**  
> или **«автоисследование по карточке …»** / **card-autoresearch**

Также: «запусти с мониторингом и дебаггером», «руководитель / исследователь /
дебаггер» по карточке канбана.

При таком триггере **не** сводить работу к одному короткому koi-execute-card:
запускай полный цикл ролей ниже.

## Три роли

| Роль | Делает | Не делает |
|------|--------|-----------|
| **0. Руководитель** | одна карточка → `running`; live-поля; state JSON; передаёт Исследователю | не запускает job, не чинит код |
| **1. Исследователь** | старт job (через project-скилл/скрипты); watch; `[x]` в §3; вызывает Дебаггера; `done` | не меняет чужой код без явного одобрения человека |
| **2. Дебаггер** | triage логов / sysmon; рекомендация в `state.debugger` | **не** правит файлы и **не** перезапускает job |

Плейбуки: [agents/manager.md](agents/manager.md),
[agents/researcher.md](agents/researcher.md),
[agents/debugger.md](agents/debugger.md).

## Cadence (по умолчанию)

| Кто | Как часто | Зачем |
|-----|-----------|-------|
| Руководитель | **один раз** в начале | карточка, live, state |
| Исследователь (watch) | **1 мин × 20**, потом **каждые 20 мин** | пульс job, `live_note`, вызов дебаггера |
| Дебаггер | **каждые 10 мин** + сразу при старте | плановый triage |
| Дебаггер | **по вызову** Исследователя | ранняя ошибка, не ждать 10 мин |
| sysmon (не агент) | по возможности **~60 с** | GPU/RAM/disk или аналог для среды |

Конкретные `*.sh` / пути логов задаёт project-specific скилл. Если его нет —
Исследователь всё равно ведёт cadence вручную (таймеры IDE / loop skill) и
пишет `live_note` в карточку/отчёт.

## Быстрый старт

```text
Пользователь: «Проведи системное исследование по карточке <id>»

Руководитель:
  1. Найти карточку → backlog → running (koi-execute-card)
  2. Live-поля + state/<project>-<card>.json
  3. Ответить человеку и передать Исследователю

Исследователь:
  1. Подключить project-скилл запуска (если есть) или локальный прогон
  2. Watch по cadence; при сбое → вызвать Дебаггера
  3. Читать state.debugger.pending_recommendation; чинить / рестартить
  4. [x] подзадачи; отчёт; running → done; koi-done-research
```

## Live-окно ResearchOS UI

Руководитель пишет в description карточки или в начало отчёта (пути от корня
проекта с кодом):

```text
live_log: projectcode/runs/live/train.log
metrics_dir: projectcode/runs/plots
live_note: старт, ждём первые шаги
live_sysmon: projectcode/runs/live/sysmon.log
compute_cost: wall_h=…; gpu_h=…; n_gpus=…; until=…; source=measured
```

Пока карточка в `running`, UI читает эти пути (🔍 на карте метода).  
`compute_cost:` — опционально; на финише job заполнить wall/GPU-h (см. **koi-execute-card**).

## State-файл

Рекомендуемый путь (рядом с project-скиллом или в `.run/` проекта):

`state/<project_id>-<card_id>.json`

Минимум полей:

```json
{
  "project_id": "<id>",
  "card_id": "<id>",
  "training_status": "running",
  "researcher_watch": {
    "phase": "warmup",
    "tick": 0,
    "last_check": null,
    "last_summary": null
  },
  "debugger": {
    "last_check": null,
    "pending_recommendation": null
  }
}
```

Дебаггер пишет рекомендацию в `debugger.pending_recommendation`; Исследователь
на watch читает, применяет или эскалирует человеку, затем сбрасывает pending.

## Связь с другими скиллами

- **koi-execute-card** — обязательный каркас канбана / §3 / отчёта / done
- **koi-report-review** — качество отчёта на фазах постановки и результатов
- **koi-done-research** — после `done`
- **koi-project-sync** — после значимых изменений
- Project-specific (пример): **verl-experiment-run** — скрипты remote/sysmon/debugger loops для verl

## Запрещено

- Брать две карточки в один autoresearch-run
- Дебаггеру править код или рестартить job
- Руководителю запускать обучение
- Закрывать `done` при незакрытых подзадачах §3 без явного open/отказа в отчёте
