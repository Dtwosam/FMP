# Phase 8A — EXP-065 One-Shot Historical Result Slot Authorization

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY SLOT AUTHORIZATION / DISPATCH LOCKED  
**Decision:** DEC-465  
**Experiment:** EXP-20261001-065  
**Predecessor:** DEC-464

## Purpose

DEC-465 opens exactly one **source-level** historical-result slot for EXP-065 while
keeping dispatch, historical execution, historical result production, rerun,
retry, replacement, reserve access, candidate compilation, promotion, Phase 8B,
broker/order activity, real-money activity, and trading locked.

This decision does not dispatch the installed workflow and does not make the
locked DEC-464 runtime executable.

## Frozen predecessor identity

DEC-465 binds merged DEC-464 commit:

`698e3e21d7dd0cbe83c3ed7d15f5544cf9c096e9`.

Exact source dependencies:

- locked runtime source:
  `717b43e3bfd656b51e22819cf948f8cd6485f334`;
- active workflow:
  `75d0e4df56d5c4ced5aff614e236cf0e1bb078e1`;
- dormant workflow template:
  `75d0e4df56d5c4ced5aff614e236cf0e1bb078e1`;
- locked CLI:
  `38e3eb9a5c2733655c845291d6bc3160e5fa0291`;
- DEC-463 evidence contract:
  `ca68622ddfc9866f00569d558b2ab927be23686d`;
- DEC-462 pairwise-interaction miner:
  `7dac382838d2b8fcc4df5d02c4949ad65c17635b`;
- repaired DEC-461 pairwise-interaction protocol:
  `b54267d790667659749a96123ad23a491ff50dfa`.

Any drift in these dependencies fails closed.

## Exact workflow identity

The only run capable of consuming the slot is a workflow run matching all of:

- name: `phase8a-exp065-pairwise-interaction`;
- path:
  `.github/workflows/phase8a-exp065-pairwise-interaction.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- run number: exactly `1`;
- run attempt: exactly `1`.

Unrelated workflow runs do not consume the slot.

## Slot inventory semantics

The source contract classifies the supplied GitHub workflow-run inventory.

### No matching run

If there is no matching manual-main EXP-065 run:

- stage is `EXP065_HISTORICAL_RESULT_SLOT_AVAILABLE`;
- attempt count is zero;
- the slot is not consumed;
- source-level slot authorization is true;
- dispatch/execution/result authorization remain false.

The built authorization contract then reports:

`EXP065_ONE_SHOT_SLOT_SOURCE_AUTHORIZED_DISPATCH_LOCKED`.

### First matching run

The first matching run consumes the slot immediately, regardless of whether it is:

- queued;
- in progress;
- completed successfully;
- completed unsuccessfully;
- cancelled.

Once present, the stage becomes:

`EXP065_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED`.

The slot remains consumed even if the run produces no usable evidence.

### More than one attempt

The contract fails closed if:

- more than one matching run exists;
- run number is not 1;
- run attempt is not 1;
- a terminal run lacks a conclusion;
- a non-terminal run reports a conclusion;
- run identity is malformed.

No second attempt, retry, rerun, or replacement path exists.

## Chronology

The one-shot historical slot is bounded to the already-seen design period:

- start: `2015-01-01T00:00:00Z`;
- end exclusive: `2023-01-01T00:00:00Z`.

The reserved robustness period remains closed:

- start: `2023-01-01T00:00:00Z`;
- end exclusive: `2026-08-21T00:00:00Z`.

DEC-465 does not authorize reading any reserved row.

## Authority state

DEC-465 sets only:

- `historical_result_slot_source_authorized = true`.

It keeps false:

- historical result dispatch;
- historical execution;
- historical result authorization;
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

## Source pins

Authorization source:

`src/fmp/discovery/exp065_historical_run_authorization.py`

blob:

`96aac63a75d7873e6b6508d34b983d0742858a02`.

Focused tests:

`tests/test_phase8a_exp065_historical_run_authorization.py`

blob:

`6de234057d06dc5485e2159dcf017fe3c01a25d2`.

## Next gate

After DEC-465 is merged and verified, a separate source-only decision may bind the
exact merged DEC-465 source and activate the one-shot historical execution/runtime
authorization for the single manual-main run.

DEC-465 itself provides no dispatch command and performs no historical execution.
