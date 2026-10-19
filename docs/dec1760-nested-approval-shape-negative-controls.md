# DEC-1760 — Offline diagnostic denies nested hidden approval fields

**DRAFT / NEVER MERGE / NEVER PROMOTE**. Exact-parent source-only child of PR #2006 (SHA `cfefc076425fa538f969dbfb0d099d26c481587d`).

The earlier BLOCKED-only report rejected unexpected top-level fields, but six nested records could quietly acquire an extra approval-like member while the original negative values still passed. This patch closes each of those nested shapes: annual main observation, historic predecessor, economic annual series, public admin observation, historical reauthentication and one-shot annual action. The already-checked 14-node dependency graph, 15 review gates and remaining packet objects keep their existing protections.

The **10** new tests mutate isolated temporary source documents to add forbidden approval/broker/dispatch keys or remove required negative/provenance fields. The report fails closed instead of presenting a normal coherent handoff. No authority, source amendments, actual current independent attestation, annual research, workflow dispatch, broker operation, Phase8B/demo/live or trading were enabled. The separate #779/#820/#821 administrator and runner blockers remain.

This is a source-only test/diagnostic improvement; exact-head Phase 3 and historical/general CI plus qualified independent review are required.
