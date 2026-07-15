# KOI package layers

```
koi/
  core/       Pure domain — models, markdown I/O, project migrations
  adapters/   Workspace paths, filesystem stores, git sync, agent backends
  agent_chat/ Agent-chat capability — answers, inbox, formatting, workers
  knowledge/  Project knowledge — rendering, summaries, generated artifacts
  literature/ Literature search, discovery, naming, and review workflows
  paper/      Paper artifacts, generation, comments, inbox, and compilation
  review/     Paper review agent — arXiv access, analysis, artifacts, and pipeline
  projects/   Project capability — commands, views, reports, ingest, live, kanban, sync
  laboratory/ Cross-project programs and portfolio views
  application/ Cross-feature use-cases and temporary compatibility shims
  services/   Transitional compatibility facades and remaining cross-feature use-cases
```

**Dependency rule:** `core` has no imports from `adapters`, `projects`, or `services`.
`adapters` may use `core`. Feature packages such as `projects` coordinate `core`,
`adapters`, and established services behind a capability-specific interface.

Bundled code must import from canonical paths (`koi.core.models`,
`koi.projects.commands`, …); `tests/test_architecture.py` enforces this rule.
Stabilized root shims for `core`, `adapters`, `agent_chat`, `knowledge`, `paper`,
`review`, `projects` (including report ingest), and `laboratory` have been removed.
Bundled code must import capabilities through their canonical packages.
