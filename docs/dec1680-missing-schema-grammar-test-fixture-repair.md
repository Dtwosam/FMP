# DEC-1680 — Repair missing-schema synthetic JSON construction

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit test/docs child of #1926 at `f994cc7c21309f0e76274a42769141e086506946`. No new methods (**4,705 proposed source-defined methods remain**).

The DEC-1679 missing-schema branch set `replacements["schema"] = None` and then passed the map to `_portable_top_level_members_json`, which joins serialized root-member strings. That construction could raise `TypeError` in the fixture before reaching `review_bundle_json_text`. The repair constructs the missing-schema JSON root directly from all *other* canonical root members, preserving the malformed `01` numeric token; for the other cases it continues using the proven root serialization helper.

The existing 17 tests continue to check grammar-before-inventory/schema/type/forged-approval precedence, immutable clean source, bounded JSON/stdin diagnostic parity and false protected authority. The correction is tests/docs only; no production/parser/limit/workflow/security change.

Own exact-head Phase 3/full historical-general CI and independent qualified review required. No protected originals/archive/artifacts, annual execution/retry, merging/deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
