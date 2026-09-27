# Phase 8A — EXP-061 Reviewed Failed Historical Result

**Date:** 2026-09-27  
**Status:** REVIEWED FAILURE / EXP-061 CLOSED / NO RETRY  
**Decision:** DEC-292  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-290

## Exact execution chain

DEC-289 executor:

- run id: `36335739823`;
- merged-main head: `a7b3bc2d0b196da2631b64c19331efb3af12c98e`;
- executor workflow run number: `1`;
- attempt: `1`;
- conclusion: `success`;
- dispatch-evidence artifact id: `10936194549`;
- artifact digest / downloaded ZIP SHA-256: `e7ffe1f08ce358eca210ef41397165196cb64bee31696a180c7fd02af8c68f1c`.

The dispatch evidence contains:

- `executor.json` SHA-256 `1e35f83f7b7e584c3ff13b4c6ba46d2c358bae323b06e564f069f03d4aba313c`;
- `historical-run.json` SHA-256 `3fe6a0cd0563e514d868bce9ab6076844049046f86ab87f2a8928a39e697d641`;
- `historical-runs.json` SHA-256 `e0515a6175e343e778e2a5da307889d89f808dc3978a4789716604ba001dec6f`.

`executor.json` has the GitHub CLI dispatch URL as its first line before the JSON payload. DEC-292 freezes that exact immutable shape instead of rewriting the executor after the result.

## Exact historical run

- run id: `36335879839`;
- workflow: `phase8a-exp061-discovery`;
- workflow run number: `2`;
- attempt: `1`;
- head: `a7b3bc2d0b196da2631b64c19331efb3af12c98e`;
- terminal conclusion: `failure`.

Job shape:

- preflight: success;
- all 18 historical discovery cells: failure;
- aggregate: skipped;
- total materialized jobs: 20.

Artifact shape:

- exactly one artifact;
- preflight artifact id: `10937316246`;
- name: `phase8a-exp061-preflight-a7b3bc2d0b196da2631b64c19331efb3af12c98e`;
- artifact digest / downloaded ZIP SHA-256: `e9a898df51317250944ad0a111d01d96d2081d708ea80872ed11b5cee48d356f`;
- `preflight.json` SHA-256: `d8a85a2482f1bf72128a8f019b73c59fccad612ad02722821cca1a09c7bc582d`.

No cell artifact and no aggregate artifact exists.

## Root cause

Every one of the 18 cell failures occurs in the EXP-061 feature adapter before discovery mining begins.

Eight cells fail with:

`EXP-061 continuous feature realized_vol_1h must be finite or null`

Ten cells fail with:

`EXP-061 continuous feature realized_vol_8h must be finite or null`

The accepted EXP-044 feature source contains non-finite rolling warm-up values. `FeatureObservation` correctly forbids non-finite numeric values, while the existing quantile protocol already treats unavailable/non-finite observations as missing and excludes them from quantile calibration/state assignment.

The implementation defect is therefore:

`NONFINITE_ROLLING_FEATURE_WARMUP_VALUES_NOT_NORMALIZED_AT_ADAPTER_BOUNDARY`

The research protocol itself was not executed far enough to produce any pattern result.

## Closure

EXP-061 is closed.

The run consumed the sole historical-result slot immediately on submission. DEC-292 authorizes no:

- rerun;
- retry;
- replacement run;
- candidate compilation;
- reserved 2023-2026 robustness access;
- promotion;
- Phase 8B;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading.

## Frozen implementation

Failed-result decision:

`src/fmp/discovery/historical_failed_result_decision.py`

Git blob:

`97956e30b66e62b708cbbdab66a95007ef096e70`

Focused tests:

`tests/test_phase8a_exp061_reviewed_failed_historical_result.py`

Git blob:

`d01430f485b81a9be74da1bad4be86630fea324b`

## Next gate

Any repair must use a **new experiment identity**.

The narrow repair should preserve the EXP-061 protocol and historical windows while changing only the feature-adapter boundary so non-finite continuous source values become `None` before construction of `FeatureObservation`.

That repair must be tested against real-source-compatible NaN/Inf cases and must not open 2023-2026 robustness data or any trading path.
