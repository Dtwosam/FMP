# Phase 8A — EXP-063 Historical Result Review

**Date:** 2026-09-30  
**Status:** HISTORICAL RESULT REVIEWED AND FROZEN / NO PERSISTENCE HYPOTHESES  
**Decision:** DEC-450  
**Experiment:** EXP-20260930-063  
**Predecessor:** DEC-449

## Purpose

DEC-450 freezes the terminal historical result of the one-shot EXP-063 run.

No thresholds, pattern definitions, state calibration, search bounds, ranking rules,
or persistence gates are changed.

No rerun, retry, replacement, reserved-data opening, candidate compilation, Phase
8B, promotion, or trading action is authorized.

## Frozen run identity

The only EXP-063 historical run is:

- run id: `36773288493`;
- workflow: `phase8a-exp063-persistence`;
- path: `.github/workflows/phase8a-exp063-persistence.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- head:
  `6b106e4514f6ca3f06c677aab66fb04eb37ad881`;
- run number: `1`;
- attempt: `1`;
- terminal status: `completed`;
- terminal conclusion: `success`.

This run consumed the one-shot slot permanently.

## Terminal run shape

Exactly 20 jobs completed successfully:

- one preflight;
- 18 persistence cells;
- one aggregate.

Exactly 20 artifacts exist and are non-expired.

Aggregate artifact:

- id: `11127203563`;
- name:
  `phase8a-exp063-aggregate-6b106e4514f6ca3f06c677aab66fb04eb37ad881`;
- artifact digest:
  `sha256:4d730f2dfdb6e6ef7201eb2d9ce48678f29882df8075a396254f5051425611d3`.

The downloaded aggregate JSON has SHA-256:

`c012740e856b351320cb95c06583d8db2c3120cce8d14e26e091594a505f24ad`

and canonical evidence fingerprint:

`d0562d29da38c8ee4c0d3b28c35b3de7c9c42a5157910eef319a91b67ca4be42`.

The canonical fingerprint was independently recomputed from the unsigned aggregate
object and matched exactly.

## Cell-level result

All 18 cell evidence artifacts were inspected.

Each cell reports:

- 2,075 enumerated patterns;
- 4,150 directional hypotheses;
- 0 qualifying directional hypotheses;
- 0 deduplicated directional hypotheses;
- empty persistence shortlist;
- empty frozen fingerprint inventory.

Across all 18 cells:

- enumerated patterns: `37,350`;
- directional hypotheses: `74,700`;
- qualifying directional hypotheses: `0`;
- deduplicated directional hypotheses: `0`;
- persistence shortlist count: `0`;
- frozen persistence count: `0`.

Every inspected cell evidence canonical fingerprint recomputed successfully.

## Classification

DEC-450 classifies the result as:

`NO_DIRECTIONAL_HYPOTHESIS_PASSED_FROZEN_PERSISTENCE_GATE`

This is stronger than a ranking or deduplication failure. No directional hypothesis
entered the qualifying set at all.

The classification applies only to the exact frozen EXP-063 universe and protocol:

- EURUSD / GBPUSD / USDJPY;
- 5m / 15m / 1h;
- 60m / 240m;
- frozen 20-feature + session state representation;
- one/two-dimension patterns;
- frozen DEC-444 persistence thresholds and ranking;
- already-seen 2015-2022 design evidence.

It does not establish that no market edge can exist outside that frozen research
universe.

## Evidence semantics

The aggregate remains labeled:

`RETROSPECTIVE_ALREADY_SEEN`

with:

`untouched_oos = false`

and output kind:

`RETROSPECTIVE_PERSISTENCE_PATTERN_HYPOTHESIS_NOT_VALIDATED`.

Because the persistence shortlist is empty, there are no frozen hypotheses to
carry forward.

## Reserved robustness

The reserved block remains unopened:

2023-01-01 through 2026-08-20.

DEC-450 does not authorize opening it.

With zero frozen persistence hypotheses, there is also no EXP-063 hypothesis set
available for robustness testing under the current protocol.

## Locks preserved

DEC-450 keeps false:

- rerun;
- retry;
- replacement run;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Frozen review source

Review source:

`src/fmp/discovery/exp063_historical_result_review.py`

blob:

`b572dbf4801c211b72285049654ebf4d96744cf1`.

Focused tests:

`tests/test_phase8a_exp063_historical_result_review.py`

blob:

`f9afb8d81658a55af1b044525ac1ee5654c3bcfe`.

## Next gate

The next gate is:

`EXPLICIT_POST_EXP063_RESEARCH_DIRECTION_DECISION`

Any successor research decision must treat the EXP-063 result as already-seen
evidence. It may not redefine DEC-444 retroactively, rescue failed hypotheses,
rerun EXP-063, or claim fresh validation from 2015-2022.
