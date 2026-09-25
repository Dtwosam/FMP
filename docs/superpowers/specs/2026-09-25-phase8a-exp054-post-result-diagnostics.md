# Phase 8A — EXP-054 Post-Result Diagnostics

**Date:** 2026-09-25
**Status:** APPROVED POST-RESULT DIAGNOSTIC / SUCCESSOR SOURCE DESIGN MAY OPEN
**Decision:** DEC-197
**Experiment:** EXP-20260925-054

## Frozen inputs

DEC-197 binds:

- DEC-196 merge: `fe84544b7acd3ce3a2e322b68b1ca723c216ce45`
- DEC-196 reviewed-result source blob: `17235435604bc5c0bd8950037bd8c49a0c6fb81a`
- DEC-184 diagnostic blob: `a2fce33c15422abeb8323a6e3014ebf5a3a52794`
- EXP-053 evidence fingerprint: `cb32abc0e4ecd3df8b639d77b6770e255aa87701eb19180dfdfb25c37dfe48e1`
- EXP-054 evidence fingerprint: `307b576f06c6aa2fb01a267232a0de553bfa79c1bdbe6bf5d55b2bfc3b40787c`

All experiments retain the same 54 budget variants, 28 available variants, 26 unavailable variants, and 26,392 utility-eligible selection rows.

## Cross-experiment pass counts

Aggregate-selection-pass counts progress:

- EXP-050: 3
- EXP-051: 1
- EXP-052: 1
- EXP-053: 10
- EXP-054: 2

Stable-selection-pass count remains zero in every experiment.

EXP-054's two aggregate passes are both the same cell:

- USDJPY / 5m / 60m / budget 250
- USDJPY / 5m / 60m / budget 1000

Thus EXP-054 narrows aggregate-pass breadth from six cells in EXP-053 to one cell.

## Common-cell comparison

For USDJPY / 5m / 60m, aggregate total net pips change as follows:

- budget 250: EXP-053 `-352.0` -> EXP-054 `+644.3`
- budget 500: EXP-053 `-108.6` -> EXP-054 `-7.7`
- budget 1000: EXP-053 `+485.2` -> EXP-054 `+302.3`

The EXP-054 budget-250 pass contains candidates only in 2022 H2:

`[0, 0, 0, 250]`

with per-window total net pips:

`[0.0, 0.0, 0.0, 644.3]`

This is aggregate financial improvement without temporal breadth.

For budget 1000, EXP-053 has window candidate counts:

`[0, 3, 130, 867]`

and total net pips:

`[0.0, 21.2, -67.2, 531.2]`

EXP-054 changes that to:

`[0, 3, 72, 925]`

and:

`[0.0, 21.2, 510.5, -229.4]`

The residual-bound ranking therefore improves the 2022 H1 financial sign but reduces 2022 H1 candidate share from 13% to 7.2%, while shifting more candidates into 2022 H2 where aggregate financial quality becomes negative.

## Diagnostic classification

The frozen classification is:

`RESIDUAL_BOUND_NARROWED_AGGREGATE_PASSES_AND_IMPROVED_SOME_DOWNSIDE_WINDOWS_BUT_DID_NOT_CREATE_TEMPORAL_BREADTH`

The evidence supports these conclusions:

- eligibility did not change;
- budget availability did not change;
- aggregate-pass breadth did not improve versus EXP-053;
- top-250 aggregate financial quality improved;
- top-250 temporal breadth did not improve;
- budget-1000 2022 H1 financial sign improved;
- budget-1000 2022 H1 candidate share did not improve;
- budget-1000 2022 H2 financial quality worsened;
- no selection-period temporal stability was demonstrated;
- no accepted model candidate was created.

## Authorization boundary

DEC-197 does not authorize:

- EXP-054 rerun or replacement;
- stability-share relaxation;
- stability-financial relaxation;
- removal of early stability windows;
- use of selection outcomes in ranking;
- selection-window recalibration;
- selection-window quotas;
- successor historical result execution;
- successor model fitting;
- promotion;
- shadow/demo execution;
- broker mutation;
- live orders;
- real-money action;
- trading.

Only a later successor protocol source design may open.

## Source and tests

Diagnostic source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_bound_utility_post_result_diagnostics.py`

Git blob:

`3f53e79b52d3a2e4de1e7f61e142ecc55197aa87`

Focused tests:

`tests/test_phase8a_exp054_post_result_diagnostics.py`

Git blob:

`a3509469a83d2a32adf8717a6a646671f2019f29`
