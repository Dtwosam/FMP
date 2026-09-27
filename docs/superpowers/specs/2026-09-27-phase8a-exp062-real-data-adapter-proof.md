# Phase 8A — EXP-062 Real-Data Adapter Proof

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY READ-ONLY PROOF / NO DISCOVERY RESULT  
**Decision:** DEC-294  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-293

## Purpose

DEC-294 proves the DEC-293 non-finite feature normalization against the exact accepted EXP-044 historical feature/outcome artifacts before any new historical discovery-result slot is considered.

This proof performs **adaptation only**.

It does not run the pattern miner, does not create discovery/confirmation/validation evidence, and does not authorize a historical result.

## Exact proof universe

Exactly nine pair/timeframe probes are allowed:

- EURUSD 5m, 15m, 1h;
- GBPUSD 5m, 15m, 1h;
- USDJPY 5m, 15m, 1h.

Each probe uses the exact feature/outcome artifact pair already frozen in the EXP-061 workflow plus the same accepted aggregate feature/outcome evidence artifacts.

The existing DEC-273 loader still selects exactly 96 monthly partitions per feature cell and 96 monthly partitions per outcome cell, covering 2015-01 through 2022-12 only.

No 2023+ partition is selected or opened.

## Probe behavior

For each pair/timeframe, DEC-294:

1. verifies and loads the exact DEC-273 range-limited feature/outcome frames;
2. counts raw numeric non-finite values across the 20 continuous feature columns;
3. executes the complete DEC-293 repaired adapter over the full verified frames;
4. requires feature row count to equal adapted feature observation count;
5. requires outcome row count to equal adapted outcome observation count;
6. requires exactly 96 selected feature partitions and 96 selected outcome partitions;
7. records the exact source/evidence identities;
8. emits one probe artifact.

The aggregate proof requires exactly nine unique pair/timeframe probe objects and requires the real accepted data to contain at least one raw non-finite continuous value. This proves the repaired case was actually exercised rather than merely passing synthetic tests.

## No mining

DEC-294 never invokes:

- `run_in_memory_discovery`;
- the EXP-061 `cell` command;
- aggregate discovery evidence compilation;
- any workflow dispatch.

Therefore the proof cannot produce a strategy, pattern hypothesis, candidate, or historical discovery result.

## Frozen source identities

DEC-292 failure freeze:

`src/fmp/discovery/historical_failure_result_decision.py`

Git blob:

`676116f34693f9a5a8f8403aaa93f28ac1c5bb46`

DEC-293 repaired adapter:

`src/fmp/discovery/market_learning_adapter.py`

Git blob:

`51096a72671fe28ac14044afb0bd8aa125416891`

Existing range-limited loader:

`src/fmp/discovery/range_limited_loader.py`

Git blob:

`df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`

Probe source:

`src/fmp/discovery/exp062_adapter_probe.py`

Git blob:

`579cf4ee01646e8abb686a9b060b53029527f441`

Probe CLI:

`scripts/phase8a_exp062_adapter_probe.py`

Git blob:

`40e0c90c41fd53cb8ce42416af8c7c5f2b60d138`

Proof workflow:

`.github/workflows/phase8a-exp062-adapter-proof.yml`

Git blob:

`e7e8460596e00f3eca1b1b0376823722dcdd3a09`

Focused probe tests:

`tests/test_phase8a_exp062_adapter_probe.py`

Git blob:

`a471c827040750d7b3c6b4697d1d08e54363a3d9`

Workflow safety tests:

`tests/test_phase8a_exp062_adapter_proof_workflow.py`

Git blob:

`43aaa104072b10255594a91bd443472c11144811`

## Workflow restrictions

The repository-hosted proof workflow:

- triggers only on relevant pushes to `main`;
- uses only `contents: read` and `actions: read`;
- has no `workflow_dispatch`, schedule, or pull-request trigger;
- checks out exact merged `main`;
- pins DEC-292/293, loader, probe, CLI, and runtime source identities;
- installs the pinned runtime without editable checkout;
- downloads only the exact accepted feature/outcome/evidence artifacts;
- keeps probe outputs outside the source checkout;
- requires the source checkout to remain clean;
- runs exactly nine adapter probes;
- compiles one deterministic aggregate proof.

## Locks preserved

Every cell proof and aggregate proof must report false:

- historical discovery execution;
- discovery-result production;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

After DEC-294 merges and its merged-main proof succeeds, a later reviewed-proof decision must freeze:

- proof run id/head/attempt/conclusion;
- all nine cell probe artifacts;
- aggregate proof artifact;
- exact artifact digests;
- exact per-cell row counts;
- exact raw non-finite counts;
- aggregate source identities.

Only after that reviewed proof may EXP-062 historical execution governance be considered.
