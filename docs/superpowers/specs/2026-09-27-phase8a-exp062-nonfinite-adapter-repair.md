# Phase 8A — EXP-062 Non-Finite Adapter Repair Foundation

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY IMPLEMENTATION REPAIR / EXECUTION LOCKED  
**Decision:** DEC-293  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-292 / closed EXP-061

## Purpose

EXP-062 preserves the discovery-first research semantics of EXP-061 while repairing one implementation defect revealed by the sole consumed EXP-061 historical attempt.

EXP-061 run `36335879839` failed in every cell before mining because non-finite rolling-volatility warm-up values reached `FeatureObservation`, which correctly requires continuous values to be finite or null.

DEC-293 changes only the adapter boundary:

- finite continuous values remain unchanged;
- existing nulls remain null;
- `NaN`, `+Inf`, and `-Inf` continuous values become `None`.

No feature is recalculated and no historical row is added, removed, retimed, or moved across research windows.

## New experiment identity

The repair uses:

`EXP-20260927-062`

EXP-061 remains closed and cannot be retried or relabeled.

DEC-293 is only the repaired adapter foundation. Later source work must propagate the EXP-062 identity through pattern fingerprints and evidence before any historical result can be authorized.

## Repair implementation

Source:

`src/fmp/discovery/exp062_adapter_repair.py`

Git blob:

`acec0967c85f7d1716a72a0c700313290ec8ecdd`

Focused tests:

`tests/test_phase8a_exp062_nonfinite_adapter_repair.py`

Git blob:

`c5ffa9fe4a1de9d5043ba5b132c693b650547cdb`

The repair wrapper reuses the frozen EXP-061:

- feature-frame identity/range validation;
- outcome adapter;
- processed-manifest identity checks;
- observation identity rules;
- 2015-2022 input range;
- 2023+ target exclusion.

## Real-failure reproduction

Focused tests reproduce the exact failure class observed in EXP-061:

- `realized_vol_1h = NaN`;
- `realized_vol_8h = +Inf`;
- `realized_vol_24h = -Inf`.

The legacy EXP-061 adapter still fails on that input.

The EXP-062 wrapper normalizes those values to `None` while leaving finite values unchanged and preserving existing nulls.

## Research semantics preserved

DEC-293 preserves:

- all 20 continuous feature definitions;
- session-state logic;
- discovery window 2015-2017;
- confirmation window 2018;
- validation window 2019-2022;
- 2023-2026 reserved block;
- support/economic thresholds;
- 0.5-pip primary and 1.0-pip stress costs;
- pattern depth and search caps;
- source feature/outcome artifacts.

## Locks

DEC-293 authorizes no:

- historical source/result execution;
- discovery result;
- candidate compilation;
- reserved robustness access;
- promotion;
- Phase 8B;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading.

## Next gate

Before EXP-062 can run, the experiment identity must be propagated through:

- pattern fingerprints;
- cell evidence;
- aggregate evidence;
- run contract and workflow artifact names;
- terminal review.

That identity propagation must remain backward compatible so frozen EXP-061 fingerprints/evidence continue to validate under their original defaults.
