# DEC-1417 — Fail-closed inline event trigger YAML source forms

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit test/docs child #1640 DEC-1416 at 27cf79732fe24b90f441c3fad6143acd14a3b276; +7 methods, **1,434 proposed source-defined methods**.

The earlier DEC-1416 source-trigger scanner used a regex requiring no scalar content after a two-space event key. An additional inline form such as push: {branches: [main]} or schedule: [{cron: ...}] could therefore be skipped, even though it could create an unintended automatic workflow entry point. This forward-only correction inventories all two-space event keys with or without scalar values, rejecting additional trigger names and duplicates; seven in-memory negative or canonical checks cover inline push, schedule, pull_request, workflow_call, duplicate/manual alterations. This limited source-text check still is not a general YAML evaluator and has no GitHub server-side authorization capability.

Exact-head Phase3, full historical CI and independent qualified review required. No installed annual workflow or setting changed, no historic artifact read and no protected annual dispatch, retry, merge or trading. Independently OS-enforced original no-write DEC-650/#820 and exclusive immutable run385/attempt1 admission DEC-651/#821/#779 remain BLOCKED.
