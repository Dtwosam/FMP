# Phase 8A — EXP-065 Protocol Helper Repair

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY PROTOCOL REPAIR / EXECUTION LOCKED  
**Decision:** DEC-461  
**Experiment:** EXP-20261001-065  
**Predecessor:** DEC-460

## Purpose

DEC-461 repairs two source-level helper defects in the merged DEC-460 EXP-065
pairwise-interaction protocol before any miner or historical runtime may depend on
that protocol.

DEC-461 does not change the mathematical hypothesis definition, market/data
universe, search volume, interaction formula, estimator, qualification thresholds,
ranking, deduplication, shortlist/freeze caps, chronology, or authority state.

## Frozen predecessor

DEC-461 binds merged DEC-460 commit:

`fd04cea05179bed6b33941635a60dfb8fb76ad60`.

The originally merged DEC-460 protocol source was:

`src/fmp/discovery/exp065_pairwise_interaction_protocol.py`

at blob:

`5ed8b86207076264096d5e6ac5aaf25472172407`.

Its focused test blob was:

`b50d3f62d5ee25e260403bc323317cf84a4b4d01`.

## Defect 1 — empirical-midrank helper composition

DEC-452 freezes the helper signature:

`empirical_midrank_percentile(calibration, value)`.

The DEC-460 wrapper `interaction_percentile(raw_interaction, calibration_values)`
incorrectly passed those arguments in reverse order.

DEC-461 repairs only that adapter call so the pairwise interaction percentile is
computed exactly under the already-frozen DEC-452 empirical-midrank semantics.

No percentile formula, calibration scope, tie rule, or threshold changes.

## Defect 2 — fail-closed interaction calibration

DEC-452 `rank_calibration_values(...)` returns `None` when the frozen minimum
calibration requirements are not satisfied.

The DEC-460 pair-calibration adapter attempted to call `len(...)` on that
`None`, producing an implementation TypeError rather than the intended protocol
failure.

DEC-461 makes this boundary explicit and fail-closed with a protocol `ValueError`.
The frozen requirements remain unchanged:

- at least 600 finite rows;
- at least 20 distinct interaction values.

No deficient calibration is repaired, imputed, relaxed, or made evaluable.

## Unchanged protocol

DEC-461 preserves all DEC-460 frozen values, including:

- exactly 20 continuous features;
- exactly 190 unordered distinct feature pairs;
- exactly 2 directions;
- exactly 2 interaction polarities;
- exactly 760 hypotheses per cell/horizon;
- exactly 13,680 hypotheses globally;
- 2015-2022 full-design constituent empirical-midrank calibration;
- pair interaction raw score
  `2 * (p_a - 0.5) * (p_b - 0.5)`;
- full-design empirical-midrank calibration of pair interaction scores;
- main-effect-controlled annual interaction OLS;
- incremental selected-tail residual requirement;
- the full eight-year support/stability/cost-stress gate;
- Jaccard >= 0.95 near-duplicate treatment;
- shortlist caps 3 per cell / 54 globally;
- frozen caps 1 per cell / 18 globally;
- evidence label `RETROSPECTIVE_ALREADY_SEEN`;
- `untouched_oos=false`;
- output kind
  `RETROSPECTIVE_PAIRWISE_INTERACTION_HYPOTHESIS_NOT_VALIDATED`.

## Authority boundary

DEC-461 remains source-only.

It authorizes no:

- historical source access;
- historical execution;
- historical result production;
- reserved 2023-2026 robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading.

No workflow, CLI, runtime, dispatch, or artifact path is introduced.

## Repaired source pins

Repaired protocol source:

`src/fmp/discovery/exp065_pairwise_interaction_protocol.py`

blob:

`b54267d790667659749a96123ad23a491ff50dfa`.

Focused tests:

`tests/test_phase8a_exp065_pairwise_interaction_protocol.py`

blob:

`08ea27be5b859073b9387187e6e0c55b8cdd0ffb`.

The new tests directly prove:

- correct DEC-452 helper argument ordering;
- exact empirical-midrank values for a deterministic calibration;
- explicit fail-closed behavior below the frozen interaction-calibration minimum.

## Next gate

After DEC-461 is merged and green, the next gate returns to:

`SOURCE_ONLY_EXP065_PAIRWISE_INTERACTION_MINER`.

Any miner must bind the repaired DEC-461 protocol blob, not the superseded
DEC-460 source blob.
