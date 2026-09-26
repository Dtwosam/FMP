# Phase 8A — EXP-060 Regime-Balance Implementation-Repair Protocol

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-253
**Experiment:** EXP-20260926-060

## Purpose

DEC-253 creates a new experiment identity for the exact implementation repair diagnosed in DEC-252.

It preserves EXP-059 regime-balance semantics and authorizes only the four predecessor-depth corrections required to make the existing source binding resolve to the intended breadth metadata.

## Frozen bindings

DEC-253 binds:

- DEC-252 merge: `fffe7311bfb0c14bf6936657b81ffe8a38c66414`
- DEC-252 diagnostic blob: `d73008c7faf236f915685110d6cf59988d6fc27f`
- DEC-251 result-decision blob: `c8ca7143e687494b81205556af7e317ec69937fd`
- EXP-059 regime-balance protocol blob: `cd4e790098a5c8d99ea2aa5264465b5d4b6b6acc`
- EXP-059 regime-balance training-core blob: `4f99c1d0cb18551b67cc89357ad4a3940c190cd2`

## Semantic preservation

EXP-060 retains EXP-059 unchanged for:

- chronology;
- model family and HGB structure;
- three jackknife fit regimes;
- unanimous positive-utility direction eligibility;
- pooled out-of-fit calibration;
- fit-temporal utility support;
- fit-temporal feature support;
- residual-bound utility;
- residual breadth;
- lower-tail mean;
- regime-floor utility;
- regime-balance utility;
- penalty multiplier `1.0`;
- candidate budgets `250 / 500 / 1000`;
- nine-part ranking/cutoff;
- four temporal-stability windows;
- minimum directional candidate share `0.10`;
- financial gates;
- validation;
- retrospective holdout;
- forward no-refit/no-recalibration rules.

The regime-balance score is retained, not redefined.

## Exact implementation repair

DEC-253 authorizes exactly four source-level predecessor-depth corrections:

`_predecessor._predecessor.<name>`

becomes:

`_predecessor._predecessor._predecessor.<name>`

for:

1. `FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW`
2. `FIT_TEMPORAL_RESIDUAL_BREADTH_RULE`
3. `RESIDUAL_BREADTH_ELIGIBILITY_RULE`
4. `RESIDUAL_BREADTH_POSITIVITY_RULE`

No other source dependency path may change under this protocol.

## Authorization state

DEC-253 authorizes:

- implementation dependency repair source only.

DEC-253 keeps false:

- protocol semantic change;
- model-protocol result production;
- model fit;
- historical result execution;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Source identity

Protocol:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_protocol.py`

Git blob:

`82d336250e2cdd9894afa5554c6b422e0de6b1fe`

Focused tests:

`tests/test_phase8a_exp060_implementation_repair_protocol.py`

Git blob:

`0aa76c5d88e6d3a894d1d19bb6241c24ade1b18f`

Protocol version:

`fmp-exp060-fit-temporal-residual-regime-balance-utility-implementation-repair-protocol-v1`

## Next gate

After DEC-253 is green and merged, the next safe gate is a deterministic in-memory EXP-060 training/evaluation core implementing exactly the four authorized predecessor-depth corrections and no semantic changes.

No artifact workflow, historical result execution, promotion, or trading path is authorized by DEC-253.
