# Phase 8A — EXP-062 Non-Finite Feature Normalization Repair

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY IMPLEMENTATION REPAIR / HISTORICAL EXECUTION LOCKED  
**Decision:** DEC-293  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-292 / closed EXP-061

## Purpose

EXP-062 is a new experiment identity opened only to repair the implementation defect frozen by DEC-292.

EXP-061 is not retried.

The DEC-270 research semantics remain unchanged:

- EURUSD, GBPUSD, USDJPY;
- 5m, 15m, 1h;
- 60m and 240m horizons;
- 2015-2017 discovery;
- 2018 confirmation;
- 2019-2022 validation;
- 2023-2026 reserved robustness closed;
- the same 20 continuous feature dimensions plus deterministic session state;
- the same one/two-predicate search;
- the same support, economic, shortlist, confirmation, and validation gates.

## Failure being repaired

EXP-061 historical run `36335879839` failed in all 18 cells inside:

`market_learning_adapter.adapt_feature_frame`

The adapter copied raw Polars feature values directly into `FeatureObservation`.

The Phase-5 feature dictionary defines warm-up, incomplete windows, missing cadence, non-finite required values, and invalid denominators as **null** feature values.

Persisted Polars frames may represent those missing floating-point values as IEEE `NaN` or infinity. The strict observation contract correctly rejects non-finite numbers unless they are represented as `None`.

The repair is therefore an adapter-boundary representation fix, not a change to the research hypothesis.

## Exact repair

For every name in `CONTINUOUS_FEATURES`:

- `None` remains `None`;
- finite `int` / `float` values remain unchanged;
- non-finite numeric values (`NaN`, `+inf`, `-inf`) become `None`;
- boolean or non-numeric values are not coerced and continue to fail the strict observation validator.

Session flags are copied unchanged and remain strict booleans.

Outcome values are unchanged and still must be finite.

No feature is forward-filled, backfilled, imputed, clipped, winsorized, or replaced with zero.

## Frozen implementation

Repaired adapter:

`src/fmp/discovery/market_learning_adapter.py`

Git blob:

`51096a72671fe28ac14044afb0bd8aa125416891`

Focused repair tests:

`tests/test_phase8a_exp062_nonfinite_feature_normalization.py`

Git blob:

`b9acdf3cda666ae9dae84e80cf3381471cccf358`

The repair binds the DEC-292 failure-freeze source:

`src/fmp/discovery/historical_failure_result_decision.py`

Git blob:

`676116f34693f9a5a8f8403aaa93f28ac1c5bb46`

## Test guarantees

Focused tests prove:

- `NaN` becomes `None`;
- positive infinity becomes `None`;
- negative infinity becomes `None`;
- existing `None` stays `None`;
- finite values are unchanged;
- session flags are not coerced;
- invalid non-numeric continuous values still fail closed.

## Execution boundary

DEC-293 does not create or authorize a new historical run.

Before EXP-062 can receive a historical slot, a later gate must prove the repaired adapter against the exact accepted EXP-044 source artifacts and show that every pair/timeframe can pass adaptation over the frozen 2015-2022 range without opening 2023+ history.

Historical dispatch, reserved robustness access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading remain locked.
