# Phase 8A — EXP-065 Pairwise Interaction Evidence Contract

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY EVIDENCE CONTRACT FROZEN / EXECUTION LOCKED  
**Decision:** DEC-463  
**Experiment:** EXP-20261001-065  
**Predecessor:** DEC-462

## Purpose

DEC-463 freezes the deterministic cell and aggregate evidence schema for EXP-065
before any historical runtime is considered.

It binds the merged DEC-462 in-memory pairwise miner and the repaired DEC-461
protocol. It does not add a loader, runtime, workflow, CLI, artifact writer,
dispatch path, historical result authority, reserved-data access, candidate
compilation, or trading authority.

## Frozen lineage

DEC-463 binds:

- DEC-462 merge:
  `735418cd455055a5102de6fb0d621355c4e85592`;
- DEC-462 miner blob:
  `7dac382838d2b8fcc4df5d02c4949ad65c17635b`;
- repaired DEC-461 protocol blob:
  `b54267d790667659749a96123ad23a491ff50dfa`.

The evidence payload must expose both protocol and miner identities and the exact
protocol fingerprint.

## Cell inventory

The expected evidence topology remains exactly 18 cells:

- 3 symbols: EURUSD, GBPUSD, USDJPY;
- 3 timeframes: 5m, 15m, 1h;
- 2 horizons: 60m, 240m.

Each cell evidence object has its own canonical SHA-256 fingerprint.

## Upstream identity pins

Every cell freezes:

- code commit;
- Phase 2 processed source manifest SHA-256;
- feature manifest SHA-256;
- outcome manifest SHA-256;
- feature evidence fingerprint;
- outcome evidence fingerprint.

The processed source manifest must match the repository's frozen symbol-specific
Phase 2 source identity.

For the same symbol/timeframe, feature and outcome manifests must be identical
across 60m and 240m horizons.

All 18 cells in one aggregate must share exactly one feature evidence fingerprint
and exactly one outcome evidence fingerprint.

## Feature calibration evidence

For each active constituent feature the evidence freezes:

- feature name;
- calibration row count;
- distinct value count;
- minimum;
- maximum;
- SHA-256 of the full sorted calibration vector.

Validation requires at least 600 rows and at least 20 distinct values and preserves
the frozen canonical feature ordering.

## Pair calibration evidence

For every active pair the evidence freezes:

- canonical feature A;
- canonical feature B;
- calibration row count;
- distinct value count;
- minimum;
- maximum;
- SHA-256 of the full sorted pair-interaction calibration vector.

Each pair must be one of the 190 canonical unordered DEC-460/461 pairs, both
constituents must be active, pair order must be canonical, row count must be at
least 600, and distinct count must be at least 20.

No missing or weak pair calibration can be represented as valid evidence.

## Nominal versus evaluable search contract

Every cell evidence object must record exactly:

`hypothesis_count = 760`.

This nominal count is invariant and represents all 190 pairs × 2 directions × 2
polarities.

The evidence separately records:

- evaluable hypothesis count;
- qualifying hypothesis count;
- deduplicated hypothesis count.

The evaluator enforces:

- evaluable <= active pair count × 4;
- qualifying <= evaluable;
- deduplicated <= qualifying.

A payload cannot shrink the nominal search space to its active/evaluable subset.

## Shortlist semantic validation

Each shortlist hypothesis freezes:

- exact cell identity;
- canonical feature pair;
- direction;
- polarity;
- hypothesis fingerprint;
- all eight 2015-2022 annual pairwise interaction statistics;
- all derived support, annual-sign, equal-year, lower-half, and two-year-block
  metrics.

Validation reconstructs the eight
`AnnualPairwiseInteractionStat` rows, reruns the frozen
`pairwise_interaction_gate_passes(...)` function, recomputes every derived metric,
recomputes the pair hypothesis fingerprint, and recomputes the exact frozen rank
key.

Therefore a caller cannot alter a metric and merely recompute the outer evidence
fingerprint.

## Frozen ranking and caps

The evidence validator requires shortlist rows to remain in exact DEC-460/461
ranking order.

Cell caps remain:

- shortlist <= 3;
- frozen <= 1.

Frozen hypothesis fingerprints must equal exactly the first shortlist item when a
shortlist exists.

Aggregate caps remain:

- shortlist <= 54;
- frozen <= 18.

## Aggregate contract

An aggregate is valid only with exactly one evidence object for every expected
cell.

It freezes for each cell:

- upstream manifest/evidence identities;
- cell evidence fingerprint;
- active constituent features;
- active canonical feature pairs;
- nominal/evaluable/qualifying/deduplicated counts;
- shortlist/frozen counts and fingerprints;
- output kind.

Cells are sorted deterministically by symbol, timeframe, and horizon.

Duplicate, missing, extra, malformed, unsorted, or cross-horizon-manifest-drifted
cells fail closed.

## Evidence semantics

Every cell and aggregate remains:

- `evidence_label = RETROSPECTIVE_ALREADY_SEEN`;
- `untouched_oos = false`;
- `reserved_robustness_opened = false`;
- output kind
  `RETROSPECTIVE_PAIRWISE_INTERACTION_HYPOTHESIS_NOT_VALIDATED`.

2015-2022 remains already-seen design evidence. The 2023-01-01 through 2026-08-20
reserved block remains closed.

## Authority boundary

DEC-463 keeps false:

- source access;
- historical execution;
- historical result production;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Frozen source pins

Evidence contract:

`src/fmp/discovery/exp065_evidence_contract.py`

blob:

`ca68622ddfc9866f00569d558b2ab927be23686d`.

Focused tests:

`tests/test_phase8a_exp065_evidence_contract.py`

blob:

`41930e892cf38e37160a9c7edbfc369d9fec679f`.

The focused tests cover deterministic cell evidence, nominal-search tampering,
incrementality tampering, annual-stat gate tampering, pair-calibration weakening,
frozen-inventory drift, exact 18-cell aggregation, duplicate/missing cells,
cross-horizon manifest drift, evaluable-count inflation, and downstream-authority
tampering.

## Next gate

After DEC-463 is merged and green, the next gate is:

`SOURCE_ONLY_EXP065_PAIRWISE_INTERACTION_RUNTIME_WIRING`.

That later gate may define only locked runtime wiring. It must not itself authorize
historical execution or result production.
