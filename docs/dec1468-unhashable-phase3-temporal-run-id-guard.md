# DEC-1468 — Malformed Phase3 run ID must fail closed before temporal log lookup

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child #1691 DEC-1467 at e0027cb3da8122bcd56e3c247b07f09107f2b160. Seven new unittest methods, **1,931 proposed source-defined methods**.

DEC-1467 made mandatory the proof-shape requirement that the Phase3 index occurs after its own runner checkout. One call path still passed an unvalidated caller-supplied `run.id` directly into a dictionary lookup of raw runner logs; if run ID was a JSON list or object, Python raises TypeError rather than producing a fail-closed diagnostic. Other reviewers already validate exact positive integer run IDs, but the composer must independently fail closed.

This child adds an exact `type(run_id) is int and run_id > 0` check before dictionary key lookup or temporal parser invocation. Seven negative/positive cases reject JSON list/dict, Boolean, absent and zero run IDs, preserve valid source consistency, and confirm the no-annual-authorization invariant. It modifies only synthetic tests/docs, not production or any annual workflow.

Its own head-associated PR merge-source-tree Phase3/full historical CI and qualified independent review mandatory. DEC-650/#820 actual original OS no-write and DEC-651/#821/#779 exclusive immutable 2023 run385/attempt1 server admission remain **BLOCKED**. No protected original/annual artifacts, dispatch/retry, installed workflow/security mutation, merge/deployment/trading.