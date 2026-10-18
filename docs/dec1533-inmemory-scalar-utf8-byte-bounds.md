# DEC-1533 — Bound UTF-8 byte volume of direct-memory evidence scalars

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child of #1778 at `b4e7ab0df72c4950075a927779895012db9048de`. Nine new synthetic methods, **2,563 proposed source-defined tests**.

The direct in-memory evidence graph preflight caps Unicode scalar character length at 4 million and aggregate scalar units at 16 million, but supplementary Unicode characters can occupy four UTF-8 bytes per character. Add a separate maximum of **4,000,000 UTF-8 bytes per exact plain string/bytes scalar** and **16,000,000 total scalar UTF-8 bytes** across visited graph nodes, retaining prior node/depth, type, Unicode-scalar and integer limits. The preflight returns false on encoding failure or byte budget exhaustion and emits only `BUNDLE_STRUCTURE_BUDGET_UNREVIEWED` through its public review wrapper. This is a bounded lexical size policy, not a claim about Python internal object layout or OS memory limits.

Nine tests cover exact/over UTF-8 scalar bounds, four-byte emoji, bytes scalar, aggregate exact/over limits, map-key sizes, direct-envelope non-disclosure and a clean source-consistency-only fixture.

Exact-head Phase 3/full historical-general CI and independent qualified review required. DEC-650/#820 original protected OS no-write and DEC-651/#821/#779 immutable exclusive one-shot protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected annual dispatch/retry, originals/archives/artifacts, installed workflow/security setting changes, merges, deployment or trading.
