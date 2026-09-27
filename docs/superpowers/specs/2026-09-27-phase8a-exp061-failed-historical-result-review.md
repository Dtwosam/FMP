# Phase 8A — EXP-061 Failed Historical Result Review

**Date:** 2026-09-27  
**Status:** TERMINAL FAILURE / SLOT CONSUMED / NO RETRY  
**Decision:** DEC-291  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-290

## Exact run

The sole historical-result attempt is:

- run id: `36335879839`;
- workflow: `phase8a-exp061-discovery`;
- branch: `main`;
- head: `a7b3bc2d0b196da2631b64c19331efb3af12c98e`;
- workflow run number: `2`;
- attempt: `1`;
- conclusion: `failure`.

The DEC-289 executor was run `36335739823`, workflow run #1 / attempt 1, and successfully submitted this sole historical attempt.

## Terminal shape

DEC-290 classifies the run as:

`EXP061_HISTORICAL_RESULT_NON_SUCCESS_TERMINAL_CLOSED`

Observed jobs:

- preflight: success;
- all 18 discovery cells: failure;
- aggregate: skipped.

Only one historical-run artifact exists:

- preflight artifact id `10937316246`;
- digest `sha256:e9a898df51317250944ad0a111d01d96d2081d708ea80872ed11b5cee48d356f`;
- non-expired.

The executor evidence artifact is:

- artifact id `10936194549`;
- digest `sha256:e7ffe1f08ce358eca210ef41397165196cb64bee31696a180c7fd02af8c68f1c`;
- non-expired.

Both downloaded ZIP files independently match GitHub's recorded SHA-256 digests.

## Shared failure cause

All 18 cells passed:

- exact main/manual-dispatch checks;
- runtime authorization;
- accepted EXP-044 feature/outcome artifact download;
- artifact digest checks;
- source-root resolution.

Every cell then failed before pattern mining while adapting accepted feature rows into EXP-061 `FeatureObservation` values.

The observed fail-closed exceptions are exclusively:

- `realized_vol_1h must be finite or null`;
- `realized_vol_8h must be finite or null`.

Failure signatures by cell are frozen in:

`src/fmp/discovery/historical_failed_result_decision.py`

No discovery shortlist, confirmation-frozen set, validation result, aggregate evidence, pattern hypothesis, strategy candidate, or trading strategy was produced.

## Frozen source identities

- DEC-290 terminal review: `2df4caa00aa683b8d627d061ae806178fbd5cd9c`;
- EXP-061 market-learning adapter: `978a33554fad7e9d78b002778c4896be0af3333a`;
- miner: `495a67699eb5014e52129f0238a2737049fe38e6`;
- protocol: `63b3f0121d6a50eb9e8e62ab666d70eb91791621`;
- range-limited loader: `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`;
- run contract: `260eb6930673427266463517546969635188b143`;
- discovery workflow: `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`;
- DEC-289 executor: `82dbec289ed69e7333a90fd28ce430b024a99936`;
- DEC-289 executor workflow: `4efb80cf9eee3f7073de28531babc269d3c7a8cc`.

Failed-result review source:

`src/fmp/discovery/historical_failed_result_decision.py`

Git blob:

`deb4a1d314b7e106deee71b6f82f79d0cddd8a9b`

Focused tests:

`tests/test_phase8a_exp061_failed_historical_result.py`

Git blob:

`d622bf703ed2127f2721036801a116ecbfc500cd`

## Disposition

EXP-061 is closed as a failed historical attempt.

- historical slot consumed: yes;
- rerun: forbidden;
- retry: forbidden;
- replacement run under EXP-061: forbidden;
- reserved 2023-2026 robustness access: closed;
- candidate compilation: locked;
- Phase 8B/demo/live/real-money/trading: locked.

## Next experiment

The failure is an adapter-boundary compatibility defect, not market evidence.

A new experiment identity may make one narrow semantic repair:

- convert floating-point `NaN` values from accepted continuous feature columns to `None` at the EXP-061-style adapter boundary;
- continue rejecting positive/negative infinity and all other invalid values;
- do not change feature definitions, cutpoints, search space, ranking, confirmation, validation, costs, data ranges, or reserved-data locks.

That repaired experiment must receive a new immutable identity and fresh one-shot historical slot. It is not an EXP-061 retry.
