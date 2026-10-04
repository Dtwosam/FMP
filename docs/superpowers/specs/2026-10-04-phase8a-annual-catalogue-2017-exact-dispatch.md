# Phase 8A — Exact 2017 Run-379 Dispatch

**Date:** 2026-10-04  
**Status:** SOURCE-DESIGN ONLY / PENDING CONCRETE DEC-542  
**Decision:** DEC-543

## Purpose

DEC-543 is the only gate that may submit the annual-catalogue workflow for
segment `2017`. It is not live until concrete DEC-542 evidence exists and the
DEC-544 reviewer is already installed on `main`.

## Preconditions

Immediately before dispatch, the executor must prove:

- current `main` is the exact DEC-542-approved head;
- active annual workflow blob is
  `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`;
- installed 2017 gate blob is
  `c1853eeec55ee98b3155a6054f07cf360793ba9b`;
- installed runtime blob is
  `e9cbc76dc9e6866e80088d223498fbcc3b870fd1`;
- concrete DEC-541 authorization and DEC-542 final preflight fingerprints match;
- annual workflow inventory is exactly runs `1, 376, 377, 378`;
- no annual run `379+` exists.

## Sole permitted action

Exactly one command surface may submit:

- ref: `main`;
- `annual_segment_label=2017`;
- `previous_annual_freeze_run_id=37206992367`.

After submission, the executor must resolve exactly one annual workflow:

- run number `379`;
- run attempt `1`;
- event `workflow_dispatch`;
- branch `main`;
- head equal to the approved main head.

Any run `380+` must fail the executor.

## Receipt

The immutable DEC-543 receipt may claim only submission:

- `dispatch_submitted = true`;
- `result_claimed = false`;
- exact run ID / run number / attempt / head;
- exact predecessor run ID;
- exact DEC-541/542 provenance.

It must keep rerun, retry, replacement, run 380+, 2018+, cross-year synthesis,
Strategy V1, promotion, Phase 8B, broker mutation, demo/live orders, real-money,
and trading authority false.

## Next gate

`REVIEW_2017_RUN_379_BEFORE_ANY_2018_EXECUTION`
