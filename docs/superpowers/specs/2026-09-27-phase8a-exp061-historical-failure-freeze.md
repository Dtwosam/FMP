# Phase 8A — EXP-061 Historical Failure Freeze

**Date:** 2026-09-27  
**Status:** TERMINAL FAILURE FROZEN / NO RETRY  
**Decision:** DEC-292  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-290

## Exact execution

The one-shot DEC-289 executor ran successfully:

- executor run id: `36335739823`;
- executor workflow run number: `1`;
- executor attempt: `1`;
- head: `a7b3bc2d0b196da2631b64c19331efb3af12c98e`;
- conclusion: `success`.

Its exact evidence artifact is:

- id: `10936194549`;
- digest: `sha256:e7ffe1f08ce358eca210ef41397165196cb64bee31696a180c7fd02af8c68f1c`.

The artifact independently hashes to the same ZIP SHA-256 and contains:

- `executor.json` SHA-256 `1e35f83f7b7e584c3ff13b4c6ba46d2c358bae323b06e564f069f03d4aba313c`;
- `historical-run.json` SHA-256 `3fe6a0cd0563e514d868bce9ab6076844049046f86ab87f2a8928a39e697d641`;
- `historical-runs.json` SHA-256 `e0515a6175e343e778e2a5da307889d89f808dc3978a4789716604ba001dec6f`.

The executor evidence proves the historical slot transitioned from zero attempts/unconsumed to one submitted attempt/consumed.

## Exact historical run

The sole EXP-061 historical-result attempt is:

- run id: `36335879839`;
- workflow run number: `2`;
- attempt: `1`;
- head: `a7b3bc2d0b196da2631b64c19331efb3af12c98e`;
- status: `completed`;
- conclusion: `failure`.

DEC-290 classifies this as:

`EXP061_HISTORICAL_RESULT_NON_SUCCESS_TERMINAL_CLOSED`

The exact terminal shape is:

- preflight: success;
- 18/18 discovery cell jobs: failure;
- aggregate: skipped;
- materialized jobs: 20;
- persisted artifacts: 1;
- cell artifacts: 0;
- aggregate artifact: 0;
- historical slot consumed: true.

The sole run artifact is the preflight artifact:

- id: `10937316246`;
- name: `phase8a-exp061-preflight-a7b3bc2d0b196da2631b64c19331efb3af12c98e`;
- digest: `sha256:e9a898df51317250944ad0a111d01d96d2081d708ea80872ed11b5cee48d356f`;
- `preflight.json` SHA-256: `d8a85a2482f1bf72128a8f019b73c59fccad612ad02722821cca1a09c7bc582d`.

## Failure diagnosis

The failure occurred after:

- exact accepted source artifacts downloaded successfully;
- source roots resolved successfully;
- DEC-285 runtime authorization passed successfully.

Representative cells across EURUSD, GBPUSD, and USDJPY fail inside:

`market_learning_adapter.adapt_feature_frame`

while creating `FeatureObservation`.

Observed failure signatures include:

- `EXP-061 continuous feature realized_vol_1h must be finite or null`;
- `EXP-061 continuous feature realized_vol_8h must be finite or null`.

The Phase 5 feature dictionary explicitly defines warm-up, missing cadence, incomplete required bars, non-finite required values, and invalid denominators as **null** outputs.

The EXP-061 adapter currently forwards raw Polars row values unchanged. IEEE `NaN` therefore reaches the stricter `FeatureObservation` validator instead of being normalized to `None`.

DEC-292 therefore classifies the failure as:

`NONFINITE_FEATURE_WARMUP_NOT_NORMALIZED`

This is an implementation/input-normalization failure, not evidence that the discovery protocol found zero profitable patterns.

## Experiment meaning

EXP-061 produced **no market-learning result**.

It cannot be interpreted as:

- zero validated patterns;
- a negative strategy result;
- a successful discovery run.

No cell evidence and no aggregate evidence exist.

The EXP-061 run slot is consumed permanently. No rerun, retry, or replacement is authorized under EXP-061.

Any repair must use a new experiment identity.

## Frozen implementation

Failure-freeze source:

`src/fmp/discovery/historical_failure_result_decision.py`

Git blob:

`676116f34693f9a5a8f8403aaa93f28ac1c5bb46`

Focused tests:

`tests/test_phase8a_exp061_historical_failure_freeze.py`

Git blob:

`f8f89536886a9ea9d80cebf755691bcba853117e`

## Downstream locks

Still false:

- EXP-061 rerun/retry/replacement;
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

Open a new EXP-062 repair identity.

The repair should be intentionally narrow:

- preserve the DEC-270 discovery/confirmation/validation semantics;
- preserve exact source artifacts and 2015-2022 historical bounds;
- normalize non-finite continuous feature values that represent Phase-5 missing/warm-up states to `None` before constructing `FeatureObservation`;
- keep session booleans strict;
- keep outcome values finite;
- add tests for `NaN` and infinities so only the intended missing-feature representation is normalized;
- prove the repair on source/test fixtures before any new historical execution slot is considered.

