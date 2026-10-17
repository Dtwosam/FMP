# DEC-1503 — Scalar resource bounds for direct offline evidence graphs

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent tests/docs child of #1748 at `c89287db17e6257b0a530c20f469bd1e3fe9171d`. Adds **10 synthetic unittest methods**; **2,274 proposed source-defined methods**.

DEC-1502 bounds the number/depth of nodes in directly supplied Python evidence, but a single plain text or bytes scalar can still be extremely large and will be counted as just one graph node. Extend its iterative preflight to count plain `str` and `bytes` keys/values as scalar units, reject any scalar longer than 4,000,000 code points/bytes and reject cumulative scalar units greater than 16,000,000. Apply the same budget to keys, nested containers and direct in-memory entry points. Existing JSON/stdin text-size, source-map, and per-run log limits remain unchanged. An oversized graph produces only the existing sanitized `BUNDLE_STRUCTURE_BUDGET_UNREVIEWED` diagnostic before nested review.

Ten synthetic tests cover exact and over-limit string/bytes values, dictionary keys, tuple/list nesting, aggregate scalar budgets, direct-envelope rejection without evidence echo, and the clean source-consistency-only fixture. No protected annual execution authority, provider authenticity or original filesystem protection is established.

Own exact-commit Phase 3/full historical-general CI plus qualified independent review required. DEC-650/#820 independently witnessed protected-original OS no-write and DEC-651/#821/#779 exclusive immutable one-shot protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected dispatch/retry, original/archive/artifact access, workflow/security changes, merge, deployment or trading.
