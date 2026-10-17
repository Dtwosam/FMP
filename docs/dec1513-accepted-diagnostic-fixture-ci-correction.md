# DEC-1513 — Correct inherited accepted-diagnostic CI fixture

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent tests/docs child of #1758 (`46039558257feac7ff158510ee57317e9f09db0c`). Eight new synthetic methods, **2,370 proposed source-defined tests**.

Full historical/general CI at #1754 and #1758 failed the same inherited `test_sorted_unique_negative_diagnostics_are_retained`: it expected mock reviewer messages `A_ERROR` and `Z_ERROR` to pass, despite DEC-1508 intentionally replacing a permissive regex with a static allowlist of actually reviewed diagnostic codes. The correct contract is that an alphabetically sorted, duplicate-free tuple **of known source-review errors** is retained, while arbitrary error strings fail closed. Replace the two made-up codes in the positive fixture with `MERGE_HISTORICAL_RUN_UNREVIEWED` and `TREE_CHAIN_ROOT_SHA_UNREVIEWED`, preserving the allowlist and its security boundary.

Eight tests show accepted known sorted codes, refused unknown/mixed/reversed/duplicate codes, zero annual authority under negative source reviews, and a clean synthetic source-only success. No provider origin verification, original OS no-write evidence or execution gate is conferred.

Exact-head Phase 3 and full historical/general CI plus independent qualified review remain mandatory. DEC-650/#820 protected-original independently witnessed OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected annual dispatch/retry, originals/archive/artifact access, installed workflows/security modifications, merges, deployment or trading.
