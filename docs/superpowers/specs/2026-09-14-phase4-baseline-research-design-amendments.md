# Phase 4 Baseline Research Design — Self-Review Amendments

**Date:** 2026-09-14  
**Applies to:** `2026-09-14-phase4-baseline-research-design.md`  
**Precedence:** this file overrides conflicting wording in the original design spec.

## Amendment 1 — review status

The design is **DRAFT FOR WRITTEN-SPEC REVIEW**. Implementation has not started. The in-chat design was approved, but the written spec still requires the normal review gate before an implementation plan is created.

## Amendment 2 — session-breakout target anchoring

Section 10.6 is amended so the target is anchored to the fully closed qualifying breakout bar, not to the session boundary.

Let `signal_mid_close` be the midpoint close of the first qualifying fully closed breakout bar.

- LONG stop remains the frozen session range low.
- LONG target is `signal_mid_close + target_range_multiple * range_width`.
- SHORT stop remains the frozen session range high.
- SHORT target is `signal_mid_close - target_range_multiple * range_width`.

Stop and target freeze when the signal becomes known. They are never rewritten after the next bar is observed. If the next executable reference price gaps through the frozen target and Phase 3 validity rules reject the order, preserve that rejection explicitly rather than moving the target.

The implementation test list is correspondingly amended to require signal-close-anchored target math and gap-beyond-target rejection without target rewriting.

## Amendment 3 — scheduled exit wording

A scheduled exit requires an exact supplied-bar timestamp match. If no exact eligible exit bar exists for the declared 16:00 Europe/London cutoff, the candidate is rejected rather than shifting the cutoff.

All other architecture, split, parameter-grid, cost, risk, reporting, non-goal, safety, and Phase 4 acceptance-boundary sections in the original design remain unchanged.