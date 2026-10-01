# Phase 8A — EXP-065 One-Shot Runtime Activation

**Date:** 2026-10-01  
**Status:** ONE-SHOT HISTORICAL RUNTIME AUTHORIZED / NOT DISPATCHED  
**Decision:** DEC-466  
**Experiment:** EXP-20261001-065  
**Predecessor:** DEC-465

## Purpose

DEC-466 is the final source-only pre-run activation for EXP-065.

It activates the already-installed DEC-464 pairwise-interaction workflow for exactly
one historical 2015-2022 run, bound to the DEC-465 one-shot slot. It also provides
a read-only dispatch operator that can produce the exact manual command only while
the slot is still unused and the inspected main head matches the expected commit.

DEC-466 does not itself dispatch the workflow.

## Frozen research/runtime lineage

The activation binds:

- DEC-465 merged commit:
  `c44d787eff659838f904955ccf95dc69a43a852d`;
- DEC-465 one-shot authorization blob:
  `96aac63a75d7873e6b6508d34b983d0742858a02`;
- DEC-464 runtime source:
  `717b43e3bfd656b51e22819cf948f8cd6485f334`;
- unchanged active workflow and dormant template:
  `75d0e4df56d5c4ced5aff614e236cf0e1bb078e1`;
- DEC-463 evidence contract:
  `ca68622ddfc9866f00569d558b2ab927be23686d`;
- DEC-462 pairwise-interaction miner:
  `7dac382838d2b8fcc4df5d02c4949ad65c17635b`;
- repaired DEC-461 pairwise-interaction protocol:
  `b54267d790667659749a96123ad23a491ff50dfa`;
- EXP-062 non-finite→null adapter:
  `491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`;
- range-limited loader:
  `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`;
- pinned runtime requirements:
  `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

Activated CLI:

`scripts/phase8a_exp065.py`

blob:

`4448d1bf43ce1ddb9dba9c4d38bb18829b95ae38`.

Runtime authorization source:

`src/fmp/discovery/exp065_historical_execution_authorization.py`

blob:

`ccc99179a51145534e1b48b8520b2f743580c217`.

Read-only dispatch operator:

`src/fmp/discovery/exp065_historical_dispatch_operator.py`

blob:

`6a386c556e121d959ec1ea8bbb56dbb49b42dde2`.

Focused activation tests:

`tests/test_phase8a_exp065_historical_runtime_activation.py`

blob:

`332bd77b57f0fa5f6b5fb5f3bb9810fbde0c2eb2`.

Successor-transition predecessor tests are narrowed without changing their frozen
decision semantics:

- DEC-464 runtime-wiring tests:
  `d1d127690a2ee5da03e6aad3dd17887c71c5dab4`;
- DEC-465 slot-authorization tests:
  `437c06778fc37464a92b98aa87a7b1fc05fd7510`.

## Successor transition

DEC-464 and DEC-465 remain immutable records of the pre-activation state.

Their source modules still report their original locked predecessor authorities.
DEC-466 does not rewrite those historical decisions.

The live CLI now imports the DEC-466 authorization gate. Predecessor tests that
previously treated the current CLI path as a byte-for-byte validation target are
therefore narrowed to their still-valid frozen workflow, lineage, topology, and
slot semantics. DEC-466 owns live-current CLI validation from this point forward.

The active workflow itself is unchanged and remains byte-identical to the dormant
DEC-464 template.

## Runtime authorization

DEC-466 authorizes historical execution only when every runtime identity matches:

- `GITHUB_ACTIONS=true`;
- repository `Dtwosam/FMP`;
- workflow `phase8a-exp065-pairwise-interaction`;
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

DEC-466 sets true only for the historical EXP-065 result surface:

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
- the DEC-465 inventory reports zero matching EXP-065 runs;
- the one-shot slot is unconsumed.

The exact planned command is:

`gh workflow run phase8a-exp065-pairwise-interaction.yml --ref main`

If any matching run already exists, the operator emits no command and reports:

`EXP065_ONE_SHOT_SLOT_CONSUMED_REVIEW_REQUIRED`

No second dispatch is planned.

## Data boundary

The authorized historical run remains limited to already-seen design evidence:

2015-01-01 through 2022-12-31.

The reserved robustness block remains closed:

2023-01-01 through 2026-08-20.

No DEC-466 authority can open that block.

## Pre-dispatch requirement

After DEC-466 merges, any actual dispatch requires a separate explicit governance
decision. A generic source-only continuation is not itself a dispatch command.

Immediately before any separately authorized dispatch, a read-only check must
confirm:

- main is still the exact DEC-466 merged head selected for dispatch;
- the EXP-065 workflow still has zero manual-main runs;
- expected run number remains 1;
- expected run attempt remains 1;
- the read-only operator returns `EXP065_ONE_SHOT_DISPATCH_READY`.

The first created run consumes the slot immediately, before its outcome is known.

## Result handling

After any separately authorized dispatch, no rerun/retry/replacement is permitted.

The next action would be immutable run/result review:

- identify the single run id/head;
- inspect all 20 expected jobs;
- inspect all expected artifacts;
- validate all 18 cell artifacts and aggregate DEC-463 evidence;
- record nominal/evaluable/qualifying/deduplicated/shortlist/frozen counts;
- freeze all evidence/protocol/source fingerprints;
- classify the historical result without redefining DEC-461/460 thresholds.

Even a workflow failure consumes the slot and proceeds to review rather than retry.

## Final boundary

DEC-466 authorizes only the one-shot historical research execution surface.

It does not execute that run, does not create an executable trading strategy, and
does not authorize any order, broker mutation, Phase 8B activity, candidate
promotion, or use of 2023-2026 reserved robustness data.

Next gate: `EXPLICIT_EXP065_ONE_SHOT_HISTORICAL_DISPATCH_DECISION`.
