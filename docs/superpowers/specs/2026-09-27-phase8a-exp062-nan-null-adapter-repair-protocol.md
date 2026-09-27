# Phase 8A — EXP-062 NaN-to-Null Adapter Repair Protocol

**Date:** 2026-09-27  
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE  
**Decision:** DEC-292  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-291 / EXP-061

## Purpose

DEC-292 creates a new experiment identity after EXP-061 failed before pattern mining.

It preserves the exact EXP-061 discovery semantics and authorizes only one adapter compatibility repair:

`float NaN -> None`

for continuous feature values immediately before `FeatureObservation` construction.

EXP-062 is not an EXP-061 retry.

## Frozen predecessor

DEC-292 binds:

- DEC-291 failed-result source blob `deb4a1d314b7e106deee71b6f82f79d0cddd8a9b`;
- EXP-061 protocol blob `63b3f0121d6a50eb9e8e62ab666d70eb91791621`;
- EXP-061 adapter blob `978a33554fad7e9d78b002778c4896be0af3333a`.

The semantic predecessor is:

- experiment `EXP-20260927-061`;
- protocol decision `DEC-270`;
- protocol version `fmp-exp061-pattern-discovery-protocol-v1`;
- exact predecessor protocol fingerprint.

## Semantic preservation

EXP-062 retains EXP-061 unchanged for:

- symbols, timeframes, horizons, and 18-cell universe;
- 2015-2017 discovery;
- 2018 confirmation;
- 2019-2022 validation;
- reserved 2023-2026 robustness closure;
- all 20 continuous features and deterministic session state;
- empirical-tertile state construction;
- one/two-predicate search;
- maximum search volume;
- discovery support/economic gates;
- 0.5-pip primary and 1.0-pip stress costs;
- ranking;
- Jaccard deduplication;
- confirmation without reranking;
- frozen validation;
- pattern-fingerprint semantics.

No research threshold, ranking rule, feature definition, outcome definition, or chronology rule changes.

## Exact implementation repair

At the continuous-feature adapter boundary only:

- if a value is a floating-point NaN, convert it to `None`;
- finite numeric values remain byte/number-equivalent;
- positive infinity remains invalid;
- negative infinity remains invalid;
- session flags are unchanged;
- observation identity is unchanged;
- feature/outcome manifest binding is unchanged.

The observed EXP-061 failure fields are:

- `realized_vol_1h`;
- `realized_vol_8h`.

The repair is generic across continuous feature columns because missing rolling-window values may occur in any continuous field, but it authorizes only NaN-as-missing normalization—not arbitrary coercion.

## Authorization

DEC-292 authorizes:

- source-only NaN-to-null adapter repair.

DEC-292 keeps false:

- protocol semantics change;
- historical result execution;
- discovery result production;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Source identity

Repair protocol:

`src/fmp/discovery/nan_null_repair_protocol.py`

Git blob:

`1d26da24134c825e2f405224316e1dd3136a38fb`

Focused tests:

`tests/test_phase8a_exp062_nan_null_repair_protocol.py`

Git blob:

`8acd25f0e97ff7b59bc21d76383735f620302ecb`

Protocol version:

`fmp-exp062-nan-null-adapter-repair-protocol-v1`

## Next gate

After DEC-292 is green and merged, the next safe gate is the repaired EXP-062 adapter/evidence implementation.

That implementation must prove:

- NaN becomes `None`;
- infinity still fails;
- finite values and session flags are unchanged;
- observation identities remain unchanged;
- predecessor nested discovery semantics remain valid;
- execution remains locked.
