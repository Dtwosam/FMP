# DEC-1522 — Bound JSON object members before dictionary construction

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1767 at `8bc62afbc04e6ff788be1a53ac28139efbaf2c41`. Nine synthetic methods; **2,460 proposed source-defined tests**.

The strict JSON decoder's `object_pairs_hook` rejects duplicate keys, but previously built arbitrary-size dictionaries from object member lists before enforcing the offline review's category-specific caps. Reject any individual JSON object containing more than **16,384 members** before constructing its dictionary or performing nested checks. This conservative cap exceeds the existing 8,192-entry source/run maps and does not alter their more specific direct in-memory diagnostics. JSON input above the cap fails with `BUNDLE_JSON_GRAMMAR_UNREVIEWED` and never echoes arbitrary source content. This bound does not claim the JSON decoder avoided constructing its temporary pairs list.

Nine tests cover exact/over hook counts, nested/top-level oversized JSON objects, duplicate rejection, ordinary values, one-line non-disclosing stdin output and a normal source-consistency-only fixture. No original OS proof, GitHub provenance or protected annual execution consent is established.

Own exact-head Phase 3/full historical/general CI and independent qualified review required. DEC-650/#820 independently witnessed protected-original OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected dispatch/retry, originals/archives/artifact access, installed workflow/security changes, merges, deployment or trading.
