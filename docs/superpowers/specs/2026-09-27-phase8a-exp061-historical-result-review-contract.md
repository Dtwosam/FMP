# Phase 8A — EXP-061 Historical Result Terminal Review Contract

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY PREDECLARED REVIEW / NO RESULT ACCEPTANCE  
**Decision:** DEC-290  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-289

## Purpose

DEC-290 freezes how the sole EXP-061 historical run #2 will be classified before its result is observed.

It is read-only. It cannot dispatch, rerun, retry, replace, promote, demo trade, mutate a broker, place live orders, or authorize real money.

## Required run identity

The reviewed run must be:

- workflow `phase8a-exp061-discovery`;
- path `.github/workflows/phase8a-exp061-discovery.yml`;
- event `workflow_dispatch`;
- branch `main`;
- caller-supplied exact expected head;
- workflow run number `2`;
- run attempt `1`;
- terminal status `completed`;
- positive run id;
- non-empty terminal conclusion.

Any other run number or rerun attempt is rejected.

## Success terminal shape

A run whose conclusion is `success` is not automatically an accepted research result.

It must first have exactly the frozen DEC-274 success shape:

- exactly 20 materialized jobs;
- exact job names: preflight + 18 cells + aggregate;
- every job terminal `success`;
- exactly 20 artifacts;
- exact commit-scoped artifact names: preflight + 18 cell evidence artifacts + aggregate evidence;
- every artifact non-expired;
- every artifact carrying a valid SHA-256 digest;
- successful aggregate job;
- aggregate artifact present.

A structurally valid success is classified:

`SUCCESS_SHAPE_PENDING_CONTENT_REVIEW`

Historical result acceptance remains false.

Pattern-hypothesis acceptance remains false.

All 18 cell evidence files and aggregate evidence must still be downloaded, hash-checked, and semantically validated before any result can be accepted.

## Non-success terminal shape

Any terminal conclusion other than `success` is classified:

`NON_SUCCESS_SLOT_CONSUMED_NO_RETRY`

The historical slot is permanently consumed.

No rerun, retry, or replacement is authorized.

Materialized jobs must be a subset of the frozen DEC-274 inventory, plus only the known GitHub compatibility shape for an unexpanded skipped matrix placeholder:

`exp061-cell-${{ matrix.dataset.symbol }}-${{ matrix.dataset.timeframe }}-${{ matrix.dataset.horizon }}m`

If that literal placeholder appears, it must be terminal `skipped`.

Exactly one preflight job must exist.

Any preserved artifact must be one of the frozen commit-scoped DEC-274 artifact names, non-expired, uniquely identified, and SHA-256 digested.

Partial evidence remains reviewable, but cannot rescue the failed attempt or authorize another run.

## Review output

The terminal-shape reviewer records:

- decision/version;
- exact run id/head;
- workflow run number 2 / attempt 1;
- terminal conclusion/classification;
- slot consumed = true;
- materialized job count/names;
- artifact count/names;
- aggregate job success flag;
- aggregate artifact presence flag;
- whether full cell/aggregate content review is required;
- whether partial evidence review is required.

It always keeps false:

- historical result accepted;
- pattern hypotheses accepted;
- rerun;
- retry;
- replacement;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Frozen implementation

Reviewer:

`src/fmp/discovery/historical_result_review.py`

Git blob:

`08f2f79d8b820eaa0101207f54d9c7e9d8d54c17`

Read-only CLI:

`scripts/phase8a_exp061_historical_result_review.py`

Git blob:

`c6d3bb06adf00ae801d579d95d5eb24a61990a85`

Focused tests:

`tests/test_phase8a_exp061_historical_result_review.py`

Git blob:

`86d164f6133c4d20074f6ecaa6a0a0701a3c39ca`

## Next gate

After the real run #2 is terminal:

- apply DEC-290 to exact run/jobs/artifact metadata;
- if non-success, freeze the failure and partial evidence with no retry;
- if structurally successful, download and independently validate every one of the 18 cell evidence artifacts plus the aggregate evidence;
- only after content validation may a later reviewed-result decision state whether any pattern hypotheses survived the frozen confirmation/validation gates.

Candidate compilation and every trading path remain locked throughout terminal review.
