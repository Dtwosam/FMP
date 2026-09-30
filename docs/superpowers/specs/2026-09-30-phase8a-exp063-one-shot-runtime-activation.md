# Phase 8A — EXP-063 One-Shot Runtime Activation

**Date:** 2026-09-30  
**Status:** ONE-SHOT HISTORICAL RUNTIME AUTHORIZED / NOT DISPATCHED  
**Decision:** DEC-449  
**Experiment:** EXP-20260930-063  
**Predecessor:** DEC-448

## Purpose

DEC-449 is the final pre-run activation for EXP-063.

It activates the already-installed DEC-447 workflow for exactly one historical
2015-2022 run, bound to the DEC-448 one-shot slot. It also provides a read-only
dispatch operator that can produce the exact manual command only while the slot is
still unused and the inspected main head matches the expected commit.

DEC-449 does not itself dispatch the workflow.

## Frozen research/runtime lineage

The activation binds:

- DEC-448 merged commit:
  `ee38ea4224345e2ed0a2c4a4baa9913b0589c8a0`;
- DEC-448 one-shot authorization blob:
  `f6070b1ecc8951338767b24dac1f0ff9ec7a24ae`;
- unchanged active workflow blob:
  `1038beb4b704ddead4e5841a6f799858732189e6`;
- DEC-446 evidence contract:
  `e8614beb156d24584b82611db47afb8c00ece71c`;
- DEC-445 persistence miner:
  `40c49a372b35dbc113dbfb71374b1ae5fc7acc45`;
- DEC-444 persistence protocol:
  `2c781dd2811b66d2d88f008007bf5c8bcf99f14f`;
- EXP-062 non-finite→null adapter:
  `491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`;
- range-limited loader:
  `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`;
- pinned runtime requirements:
  `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

Activated CLI:

`scripts/phase8a_exp063.py`

blob:

`1ed4616af6de156fc1f832bf63b1a97c4caac8e9`.

Runtime authorization source:

`src/fmp/discovery/exp063_historical_execution_authorization.py`

blob:

`fd87ab32eafa43e2cffb305680a1747314f4f3e5`.

Read-only dispatch operator:

`src/fmp/discovery/exp063_historical_dispatch_operator.py`

blob:

`e05b502a495451efb1678034a0405855f4d199e8`.

Focused activation tests:

`tests/test_phase8a_exp063_historical_runtime_activation.py`

blob:

`ba2b3ebb81bd83accb047b29798ef757eb257800`.

## Successor transition

DEC-447 and DEC-448 remain immutable records of the pre-activation state.

Their source modules still report the locked predecessor authorities. DEC-449 does
not rewrite those historical decisions.

The live CLI now imports the DEC-449 authorization gate. Therefore predecessor
tests that previously used the current CLI path as a byte-for-byte live validation
target are narrowed to their still-valid frozen workflow, lineage, topology, and
slot semantics. DEC-449 owns live-current CLI validation from this point forward.

The active workflow itself is unchanged.

## Runtime authorization

DEC-449 authorizes historical execution only when every runtime identity matches:

- `GITHUB_ACTIONS=true`;
- repository `Dtwosam/FMP`;
- workflow `phase8a-exp063-persistence`;
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

DEC-449 sets true only for the historical EXP-063 result surface:

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
- the DEC-448 inventory reports zero matching EXP-063 runs;
- the one-shot slot is unconsumed.

The exact planned command is:

`gh workflow run phase8a-exp063-persistence.yml --ref main`

If any matching run already exists, the operator emits no command and reports:

`EXP063_ONE_SHOT_SLOT_CONSUMED_REVIEW_REQUIRED`

No second dispatch is planned.

## Data boundary

The authorized historical run remains limited to already-seen design evidence:

2015-01-01 through 2022-12-31.

The reserved robustness block remains closed:

2023-01-01 through 2026-08-20.

No DEC-449 authority can open that block.

## Pre-dispatch requirement

After DEC-449 merges, the manual dispatch must occur only after an immediate
read-only check confirms:

- main is still the DEC-449 merged head selected for dispatch;
- the EXP-063 workflow still has zero manual-main runs;
- expected run number remains 1;
- expected run attempt remains 1;
- the read-only operator returns `EXP063_ONE_SHOT_DISPATCH_READY`.

The first created run consumes the slot immediately, before its outcome is known.

## Result handling

After dispatch, no rerun/retry/replacement is permitted.

The next action is immutable run/result review:

- identify the single run id/head;
- inspect all 20 expected jobs;
- inspect all expected artifacts;
- validate cell and aggregate DEC-446 evidence;
- record the persistence shortlist/frozen counts and fingerprints;
- classify the historical result without redefining DEC-444.

Even a workflow failure consumes the slot and proceeds to review rather than retry.

## Final boundary

DEC-449 authorizes the one-shot historical research execution only.

It does not create an executable trading strategy and does not authorize any order,
broker mutation, Phase 8B activity, or use of 2023-2026 reserved robustness data.
