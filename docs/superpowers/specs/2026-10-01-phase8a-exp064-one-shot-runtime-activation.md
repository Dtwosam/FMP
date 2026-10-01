# Phase 8A — EXP-064 One-Shot Runtime Activation

**Date:** 2026-10-01  
**Status:** ONE-SHOT HISTORICAL RUNTIME AUTHORIZED / NOT DISPATCHED  
**Decision:** DEC-457  
**Experiment:** EXP-20261001-064  
**Predecessor:** DEC-456

## Purpose

DEC-457 is the final pre-run activation for EXP-064.

It activates the already-installed DEC-455 workflow for exactly one historical
2015-2022 run, bound to the DEC-456 one-shot slot. It also provides a read-only
dispatch operator that can produce the exact manual command only while the slot is
still unused and the inspected main head matches the expected commit.

DEC-457 does not itself dispatch the workflow.

## Frozen research/runtime lineage

The activation binds:

- DEC-456 merged commit:
  `ef6c40d3e8148e52256917576423a8e6f53e8cfb`;
- DEC-456 one-shot authorization blob:
  `0668910a69a87fad06be73af98e5f403436fe7fb`;
- DEC-455 runtime source:
  `07e5ccebb6416c04621aa54e170cd4eb1e0a2a04`;
- unchanged active workflow:
  `caca62672ad9796764c18be6b8da9785b98c9733`;
- DEC-454 evidence contract:
  `9aee3f9e273e20329c9de5a7079ed924ffee0a9a`;
- DEC-453 continuous-stability miner:
  `b0d799ec1afaf43b0441290c97a9f39c37ecd2fd`;
- DEC-452 continuous-stability protocol:
  `c108ea047c7bfb3e588bfbac33993180066c28ad`;
- EXP-062 non-finite→null adapter:
  `491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`;
- range-limited loader:
  `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`;
- pinned runtime requirements:
  `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

Activated CLI:

`scripts/phase8a_exp064.py`

blob:

`29fce0ac43adf6743448d5936b00f7e6755df2b4`.

Runtime authorization source:

`src/fmp/discovery/exp064_historical_execution_authorization.py`

blob:

`5d5c0e8ceeeef4b0b2d45167c47a682937ef8121`.

Read-only dispatch operator:

`src/fmp/discovery/exp064_historical_dispatch_operator.py`

blob:

`469551d56332644e53741b5aeeb8314ba934b662`.

Focused activation tests:

`tests/test_phase8a_exp064_historical_runtime_activation.py`

blob:

`af3c8b4aabd9503ab6f50ffaa99eea976bb75bb6`.

## Successor transition

DEC-455 and DEC-456 remain immutable records of the pre-activation state.

Their source modules still report the locked predecessor authorities. DEC-457 does
not rewrite those historical decisions.

The live CLI now imports the DEC-457 authorization gate. Therefore predecessor
tests that previously used the current CLI path as a byte-for-byte live validation
target are narrowed to their still-valid frozen workflow, lineage, topology, and
slot semantics. DEC-457 owns live-current CLI validation from this point forward.

The active workflow itself is unchanged.

## Runtime authorization

DEC-457 authorizes historical execution only when every runtime identity matches:

- `GITHUB_ACTIONS=true`;
- repository `Dtwosam/FMP`;
- workflow `phase8a-exp064-continuous-stability`;
- event `workflow_dispatch`;
- ref `refs/heads/main`;
- run number exactly `1`;
- run attempt exactly `1`;
- `GITHUB_SHA` equals the code commit supplied to the CLI;
- `GITHUB_RUN_ID` is a positive integer;
- all pinned source blobs match.

Run number 2 fails closed.

Run attempt 2 fails closed.

Local/non-GitHub execution fails closed.

A different repository, workflow, ref, or SHA fails closed.

## Authority opened

DEC-457 sets true only for the historical EXP-064 result surface:

- historical execution source authorization;
- one-shot slot source authorization;
- historical-result dispatch authorization;
- historical execution authorization;
- historical result production authorization.

It keeps false:

- rerun;
- retry;
- replacement;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Read-only dispatch operator

The dispatch operator has no execute mode and invokes no subprocess.

It accepts:

- current main-branch metadata;
- current workflow-run inventory;
- an expected main head SHA.

It emits the dispatch command only if:

- main is exactly at the expected head;
- the DEC-456 inventory reports zero matching EXP-064 runs;
- the one-shot slot is unconsumed.

The exact planned command is:

`gh workflow run phase8a-exp064-continuous-stability.yml --ref main`

If any matching run already exists, the operator emits no command and reports:

`EXP064_ONE_SHOT_SLOT_CONSUMED_REVIEW_REQUIRED`

No second dispatch is planned.

## Data boundary

The authorized historical run remains limited to already-seen design evidence:

2015-01-01 through 2022-12-31.

The reserved robustness block remains closed:

2023-01-01 through 2026-08-20.

No DEC-457 authority can open that block.

## Pre-dispatch requirement

After DEC-457 merges, dispatch may occur only after an immediate read-only check
confirms:

- main is still the exact DEC-457 merged head selected for dispatch;
- the EXP-064 workflow still has zero manual-main runs;
- expected run number remains 1;
- expected run attempt remains 1;
- the read-only operator returns `EXP064_ONE_SHOT_DISPATCH_READY`.

The first created run consumes the slot immediately, before its outcome is known.

## Result handling

After dispatch, no rerun/retry/replacement is permitted.

The next action is immutable run/result review:

- identify the single run id/head;
- inspect all 20 expected jobs;
- inspect all expected artifacts;
- validate cell and aggregate DEC-454 evidence;
- record shortlist/frozen counts and fingerprints;
- classify the historical result without redefining DEC-452.

Even a workflow failure consumes the slot and proceeds to review rather than retry.

## Final boundary

DEC-457 authorizes the one-shot historical research execution only.

It does not create an executable trading strategy and does not authorize any order,
broker mutation, Phase 8B activity, or use of 2023-2026 reserved robustness data.
