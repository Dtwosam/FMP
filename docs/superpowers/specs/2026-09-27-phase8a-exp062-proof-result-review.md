# Phase 8A — EXP-062 Gate-Proof Result Review

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY READ-ONLY REVIEW / NO HISTORICAL SLOT  
**Decision:** DEC-304  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-303

## Purpose

DEC-304 adds the read-only result reviewer for the one-shot fail-closed EXP-062 gate proof.

It combines:

- the exact DEC-301 terminal proof validation; and
- the exact DEC-303 proof-dispatch evidence.

It cannot dispatch, execute historical discovery, open the historical-result slot, rerun, retry, replace, compile candidates, promote, demo trade, live trade, or touch reserved robustness data.

## Required proof terminal

The proof must validate through DEC-301 as:

`EXP062_GATE_PROOF_REVIEWED_FAIL_CLOSED`

with:

- workflow run #1;
- attempt 1;
- terminal failure at the locked execution gate;
- source-ready preflight evidence;
- exactly one non-expired preflight artifact;
- zero cell-result artifacts;
- zero aggregate-result artifacts;
- no historical discovery execution;
- historical-result slot not consumed.

## Required executor evidence

DEC-304 requires DEC-303 evidence from the same exact head showing:

- the pre-dispatch DEC-302 plan had zero EXP-062 manual-main runs;
- two identical fresh plans were checked;
- the sole proof command was submitted;
- proof submission is not a historical result;
- the historical-result slot remains unconsumed;
- historical-result dispatch/execution remains false;
- rerun/retry/replacement remains false.

## Review result

A valid combined review returns:

`EXP062_GATE_PROOF_RESULT_REVIEWED_FAIL_CLOSED`

and records the exact proof run id, head, preflight artifact id/digest, materialized job shape, and known GitHub matrix-placeholder shape.

The next gate remains:

`IMMUTABLE_PROOF_RESULT_FREEZE_BEFORE_HISTORICAL_SLOT`

## Frozen implementation

Reviewer:

`src/fmp/discovery/exp062_proof_result_review.py`

Git blob:

`58ad68ba68e480d9af222c378dbdc1a32e2835c5`

Focused tests:

`tests/test_phase8a_exp062_proof_result_review.py`

Git blob:

`7a8108a4a6c506925e6a2c3f3f68e1e730210407`

## Locks preserved

DEC-304 keeps false:

- historical-result slot open authorization;
- historical-result dispatch;
- historical discovery execution;
- discovery-result production;
- rerun;
- retry;
- replacement;
- reserved 2023-2026 access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

After the actual proof exists and DEC-304 validates it, a later decision must freeze the exact proof run, preflight artifact, executor artifact, raw evidence hashes, and reviewed result.

Only that immutable freeze may be considered as a predecessor for a future EXP-062 historical-result slot.
