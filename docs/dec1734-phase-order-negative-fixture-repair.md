# DEC-1734 — Correct Phase 8A/8B order mutation as an assertion failure

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent test/docs correction to #1980 at `99a80dc7020e45d828e4f0d5958ec10d92fbdc7e`.

The DEC-1733 `test_detects_phase8b_before_research_phase8a` originally changed the Phase 8A header to an *unknown* Phase 8C header. That means DEC-1732 would raise a `ValueError` while finding a missing header, rather than the intended `AssertionError` proving it had detected **inverted phase order**. The negative-control test itself would fail for the wrong reason.

This test-fixture-only correction swaps the existing `### Phase 8A` and `### Phase 8B` headings in a private in-memory string using a temporary sentinel. It preserves both known headers, reverses their order, and makes the actual order guard assert unsorted indices, raising the expected `AssertionError`. The original build-order Markdown on disk is never changed. All other 13 DEC-1733 methods and previous source-only conditions remain unchanged. **No new test methods: 5,995 proposed total.**

All changes remain offline synthetic tests/docs, with no parser/production/workflow/admin rule, protected yearly data, annual dispatch/retry, strategy synthesis/promotion, broker or trading change. Original #1980 has a defective negative-control case; full exact-head Phase3/historical-general CI and qualified independent review must be applied to this corrected descendant. Issue #779 is still **BLOCKED**.
