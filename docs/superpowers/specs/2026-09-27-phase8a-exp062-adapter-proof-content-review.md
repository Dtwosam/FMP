# Phase 8A — EXP-062 Adapter Proof Content Review

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY PREDECLARED CONTENT REVIEW / NO PROOF RESULT YET  
**Decision:** DEC-296  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-295

## Purpose

DEC-296 defines how a complete successful DEC-294 real-data adapter proof is reviewed at the JSON-content level.

A green workflow alone is insufficient. DEC-296 must revalidate the nine cell probe objects and deterministically rebuild the aggregate proof before the repair can be considered demonstrated on accepted historical data.

This decision authorizes no mining or historical discovery execution.

## Entry requirements

DEC-296 accepts content only when DEC-295 reports:

`EXP062_ADAPTER_PROOF_SUCCESS_COMPLETE_REVIEW_REQUIRED`

The terminal review must bind the exact proof head and prove:

- push-to-main attempt 1;
- proof success complete;
- exactly 10 materialized jobs;
- exactly 10 artifacts;
- aggregate content review required;
- every execution, result, candidate, promotion, demo/live, real-money, and trading authority still false.

## Cell proof review

Exactly nine cell probe objects are required:

- EURUSD 5m / 15m / 1h;
- GBPUSD 5m / 15m / 1h;
- USDJPY 5m / 15m / 1h.

Each object is passed through the existing DEC-294 cell validator and must bind the exact proof head.

The complete cell identity set must equal the frozen nine-cell universe.

## Aggregate proof review

DEC-296 recompiles the aggregate from the nine validated cells using the frozen DEC-294 aggregate compiler.

The persisted aggregate must equal the deterministic recompilation exactly.

The aggregate must still prove:

- all nine adapter probes succeeded;
- total real raw non-finite count is greater than zero;
- feature/outcome row totals reconcile;
- each cell preserved exact adaptation row parity;
- no discovery execution/result authority exists.

DEC-296 also totals the raw non-finite counts by continuous feature and by pair/timeframe cell. These are diagnostics only and do not change the research protocol.

## Verified meaning

A successful DEC-296 review is classified:

`EXP062_ADAPTER_REPAIR_REAL_DATA_PROOF_VERIFIED`

Its meaning is limited to:

`NONFINITE_MISSING_VALUES_NORMALIZED_WITHOUT_MINING`

It does not mean that a market pattern, candidate, or profitable strategy has been found.

## Frozen implementation

Content-review source:

`src/fmp/discovery/exp062_adapter_proof_content_review.py`

Git blob:

`26529be12229953070f5dbf929699e7e86a2a9bb`

Focused tests:

`tests/test_phase8a_exp062_adapter_proof_content_review.py`

Git blob:

`0fa4c87457c49500268f577f35ee9b27729f742b`

DEC-296 consumes the DEC-295 review contract and DEC-294 probe compiler already frozen in the predecessor stack.

## Locks preserved

DEC-296 keeps false:

- historical discovery execution;
- discovery-result production;
- reserved 2023-2026 robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

Only after a real merged-main DEC-294 proof succeeds and a later result-freeze decision binds the exact run and artifact digests may DEC-296 be applied to those downloaded proof contents.

If the content review verifies the repair, a later source-only decision may define a new EXP-062 historical execution slot. That slot must be separate from closed EXP-061 and must not open reserved 2023-2026 data or candidate/trading paths.
