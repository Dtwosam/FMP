# Phase 8A — EXP-061 Historical Result Content Review

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY READ-ONLY CONTENT REVIEW / NO RESULT YET  
**Decision:** DEC-291  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-290

## Purpose

DEC-291 defines the read-only content review for a **successful and complete** EXP-061 historical run after DEC-290 has already validated its terminal run/job/artifact shape.

It does not dispatch, rerun, retry, replace, compile a trading candidate, promote, or trade.

## Entry requirements

DEC-291 accepts content only when DEC-290 reports:

`EXP061_HISTORICAL_RESULT_SUCCESS_COMPLETE_REVIEW_REQUIRED`

The terminal review must prove:

- workflow run number `2`;
- run attempt `1`;
- exact historical-run head binding;
- historical-result slot consumed;
- exact 20-job success shape;
- exact 20-artifact success shape;
- no GitHub unexpanded matrix placeholder;
- candidate compilation still locked;
- all downstream trading paths still locked.

A non-success DEC-290 result can never enter DEC-291 content review.

## Deterministic content validation

DEC-291 requires exactly 18 cell-evidence objects.

For each cell it:

- runs the existing EXP-061 cell-evidence validator;
- requires the exact historical-run code commit.

It then:

- validates the aggregate evidence through the existing DEC-274 validator;
- requires the aggregate code commit to equal the historical-run head;
- deterministically recompiles aggregate evidence from the validated 18 cells;
- requires the persisted aggregate to exactly equal that deterministic recompilation.

Any mismatch fails closed.

## Result meaning

After exact validation, DEC-291 reports:

- discovery shortlist count;
- confirmation frozen count;
- validation accepted count;
- validated pattern fingerprints;
- validated pattern fingerprints grouped by cell.

If validation accepted count is zero:

`EXP061_HISTORICAL_RESULT_REVIEWED_NO_VALIDATED_PATTERNS`

If one or more validated pattern hypotheses exist:

`EXP061_HISTORICAL_RESULT_REVIEWED_VALIDATED_PATTERN_HYPOTHESES_PRESENT`

The output meaning remains:

`PATTERN_HYPOTHESIS_NOT_EXECUTABLE_STRATEGY`

A validated pattern hypothesis is **not yet a trading strategy or candidate**.

## Frozen implementation

Content-review source:

`src/fmp/discovery/historical_result_content_review.py`

Git blob:

`cb5330815492ad8a9404a9ec0ef80ebbc13c87e4`

Focused tests:

`tests/test_phase8a_exp061_historical_result_content_review.py`

Git blob:

`624e9661f365a3b5c35cf114951d632c165edf93`

## Locks preserved

DEC-291 keeps false:

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

If DEC-291 finds zero validated patterns, EXP-061 has a valid negative historical discovery result.

If DEC-291 finds validated pattern hypotheses, the next gate is a **separate candidate-compilation protocol** that decides how frozen pattern hypotheses can be transformed into candidate strategy definitions without reusing the same validation evidence for tuning.

That later gate must remain separate from DEC-291 and cannot use the reserved 2023-2026 robustness block unless explicitly authorized by a new decision.
