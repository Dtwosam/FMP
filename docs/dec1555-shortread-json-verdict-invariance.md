# DEC-1555 — Stdin chunk-boundary JSON verdict invariance

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child of #1801 at `4495d41154f5cac24ae74f1113fa182d3acbdb01`. Eight synthetic methods plus a shared assertion helper (**2,757 proposed source-defined tests**).

Valid or invalid JSON results must not change when an input stream returns short positive text fragments. Tests cover escaped structural punctuation, Unicode escaped key aliases, malformed quoted text, small literal Unicode, over-limit ASCII-escaped Unicode, over-limit literal Unicode bytes, a valid synthetic evidence bundle, and an invalid private trailer after a valid prefix. Check one safe JSON output record, source-only status mapping, and permanently false independent OS/server/annual authority on every chunk-size variant.

No changes to source-review implementation, resource limits, protected controls, workflow or trading. Own exact-head Phase 3/full historical-general CI and independent qualified review required. DEC-650/#820 independently witnessed protected-original OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain BLOCKED. No protected originals/archives/artifacts, annual execution or retry, merge, deployment or trading.
