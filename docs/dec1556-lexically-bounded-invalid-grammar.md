# DEC-1556 — Lexically budget-safe but invalid JSON grammar refusals

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact one-commit tests/docs child of #1802 at `f7e65d4dc5d8b3ddd6160d8b78c9160cb2e8f91b`, adding eight synthetic unittest methods and a common decoder-assertion helper (**2,765 proposed source-defined tests**).

Predecoder lexical scanners are intentionally limited to nesting and resource ceilings; they do not replace standard JSON grammar validation. Exercise missing object colons, missing separators in objects/arrays, trailing commas, single-quoted keys, JavaScript-style comments, and invalid numeric tokens. Every lexically in-budget sample must reach the standard JSON decoder exactly once, be safely refused as malformed JSON, never reach the downstream source reviewer, and never confer independent protected-original proof, exclusive admission or annual-run authorization.

Own exact-head Phase 3/full historical-general CI and independent qualified review required. No parser source, resource-limit, workflow/security-control or protected-admission changes. DEC-650/#820 independent protected-original OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 admission remain BLOCKED. No protected annual runs/retries, original/archive/artifact access, merge, deployment or trading.
