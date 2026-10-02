# Phase 8A — EXP-065 Historical Result Review

**Date:** 2026-10-02  
**Status:** HISTORICAL RESULT REVIEWED AND FROZEN / NO PAIRWISE-INTERACTION QUALIFIERS  
**Decision:** DEC-468  
**Experiment:** EXP-20261001-065  
**Predecessor:** DEC-467

## Purpose

DEC-468 freezes the terminal historical result of the one-shot EXP-065 run.

EXP-065 is a bounded pairwise continuous-feature interaction sub-experiment inside the governing DEC-268 discovery-first market-pattern research framework. Freezing its negative result does not redefine or reject that broader method.

No interaction transform, estimator, stability threshold, cost rule, ranking rule, search bound, shortlist cap, or freeze cap is changed. No rerun, retry, replacement, reserved-data opening, candidate compilation, Phase 8B, promotion, or trading action is authorized.

## Frozen run identity

The only EXP-065 historical run is:

- run id: `36905224184`;
- workflow: `phase8a-exp065-pairwise-interaction`;
- path: `.github/workflows/phase8a-exp065-pairwise-interaction.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- head: `5faa733572576aa5a1c56176ac27c415eaaf6416`;
- run number: `1`;
- attempt: `1`;
- terminal status: `completed`;
- terminal conclusion: `success`.

This run consumed the one-shot slot permanently.

## Terminal run shape

Exactly 20 jobs completed successfully: one preflight, 18 pairwise-interaction cells, and one aggregate. Exactly 20 artifacts exist and are non-expired.

Aggregate artifact:

- id: `11202316160`;
- name: `phase8a-exp065-aggregate-5faa733572576aa5a1c56176ac27c415eaaf6416`;
- artifact digest: `sha256:55e3a725127a1195a23159a6f8f8e187d90443f6e4df1be213a143c8e8868214`.

The downloaded aggregate JSON SHA-256 is `080d9e36c572d570f7890b51d543cb00821ba25f76164a6c6d289d9b6ccb8a62`.

The canonical evidence fingerprint is `be0822560c0c4ec5a7dfc90e85c65d963621e04a4bd238ea078a4ac4d7a99682`. Independent recomputation from the unsigned aggregate object matched exactly.

## Cell-level result

All 18 exact EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m cell evidence artifacts were downloaded and independently recomputed.

Every cell reports 760 nominal hypotheses, 760 evaluable hypotheses, zero qualifying hypotheses, zero deduplicated hypotheses, an empty pairwise-interaction shortlist, and an empty frozen fingerprint inventory.

Across all 18 cells:

- hypotheses: `13,680`;
- evaluable hypotheses: `13,680`;
- qualifying hypotheses: `0`;
- deduplicated hypotheses: `0`;
- shortlist count: `0`;
- frozen count: `0`.

Every cell canonical evidence fingerprint recomputed successfully and matched its exact aggregate cell fingerprint. The exact 18 fingerprints are frozen in the review source.

## Frozen evidence identities

- protocol fingerprint: `437e86d53094a52445b02956498b6b1bafcc91575efad1661dddf8aefaf0c4f0`;
- feature evidence fingerprint: `1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815`;
- outcome evidence fingerprint: `b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117`.

## Classification and scope

Classification: `NO_PAIRWISE_INTERACTION_HYPOTHESIS_PASSED_FROZEN_GATE`.

DEC-467 result state: `ZERO_PAIRWISE_INTERACTION_QUALIFIERS`.

This is a negative result for the exact frozen EXP-065 pairwise-interaction representation and protocol. It says that none of the 13,680 frozen hypotheses passed the predeclared gate on already-seen 2015-2022 evidence.

It does **not** establish that discovery-first market-pattern research has failed, that no market edge exists, or that other market-behaviour representations are exhausted.

Evidence remains `RETROSPECTIVE_ALREADY_SEEN`, `untouched_oos=false`, with output kind `RETROSPECTIVE_PAIRWISE_INTERACTION_HYPOTHESIS_NOT_VALIDATED`.

## Reserved robustness and locks

The reserved 2023-01-01 through 2026-08-20 block remains unopened and unauthorized.

Rerun, retry, replacement, reserved robustness access, candidate compilation, promotion, Phase 8B, demo orders, broker mutation, live orders, real-money action, and trading all remain false.

## Discovery-first interpretation

The governing method remains DEC-268 discovery-first market-pattern research:

`market measurements -> bounded discovery -> pattern freeze -> chronological confirmation/validation -> strategy/model compilation -> robustness -> prospective shadow -> fixed-version demo -> completed-evidence learning`

EXP-065 covered one bounded question: whether exactly two existing continuous features add incremental interaction information beyond their two main effects under the frozen retrospective protocol.

A successor direction must therefore be selected by the discovery-first operating guardrail, including an explicit statement of the market behaviour being searched, the measurement vocabulary covered and omitted, the justified meaning of another negative result, and how any survivor would rejoin the main chronological workflow.

## Frozen review source

Review source `src/fmp/discovery/exp065_historical_result_review.py` is blob `12580fe033a29d4d25b61140a4cf53a7126547ea`.

Focused tests `tests/test_phase8a_exp065_historical_result_review.py` are blob `c895d49ef6e25dfabf8a03e53c7fc10143f7eea7`.

## Next gate

The next gate is `EXPLICIT_POST_EXP065_DISCOVERY_FIRST_RESEARCH_DIRECTION_DECISION`.

That gate is a research-direction decision, not automatic authorization for another transform, model family, historical run, or reserved-data access.
