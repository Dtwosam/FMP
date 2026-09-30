# Phase 8A — EXP-063 One-Shot Historical Slot Authorization

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY ONE-SHOT SLOT AUTHORIZATION / DISPATCH LOCKED  
**Decision:** DEC-448  
**Experiment:** EXP-20260930-063  
**Predecessor:** DEC-447

## Purpose

DEC-448 opens exactly one source-authorized EXP-063 historical-result slot while
keeping workflow dispatch, historical execution, and result production locked.

It does not dispatch the workflow.

## Bound runtime

DEC-448 binds merged DEC-447 commit:

`cbd7f5adce4cae062ba427bf61c3239e77dc5b72`

and exact blobs:

- runtime source:
  `6e7804a037fd386016fd45145be73b8dc00563f2`;
- active workflow:
  `1038beb4b704ddead4e5841a6f799858732189e6`;
- runtime CLI:
  `1b969668f79b37bc68f701da103b3a2bb53b13c1`;
- DEC-446 evidence contract:
  `e8614beb156d24584b82611db47afb8c00ece71c`;
- DEC-445 miner:
  `40c49a372b35dbc113dbfb71374b1ae5fc7acc45`;
- DEC-444 protocol:
  `2c781dd2811b66d2d88f008007bf5c8bcf99f14f`.

Authorization source:

`src/fmp/discovery/exp063_historical_run_authorization.py`

blob:

`f6070b1ecc8951338767b24dac1f0ff9ec7a24ae`

Focused tests:

`tests/test_phase8a_exp063_historical_run_authorization.py`

blob:

`5642d7f91092e7f23f271444df5a40b25d8a1db7`

## Current run inventory

At DEC-448 creation time, the installed
`phase8a-exp063-persistence` workflow has zero manual-main
`workflow_dispatch` runs.

Therefore no proof-run exclusion is necessary.

The first relevant manual-main workflow run is the one and only historical-result
attempt.

## Slot-consumption rule

The slot is consumed immediately when the first relevant workflow run exists.

Consumption does not wait for a terminal result.

All of the following consume the slot:

- queued;
- in progress;
- completed success;
- completed failure;
- cancellation or other terminal outcome.

A terminal failure does not authorize retry, rerun, or replacement.

The expected first run is:

- workflow: `phase8a-exp063-persistence`;
- path: `.github/workflows/phase8a-exp063-persistence.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- run number: 1;
- run attempt: 1.

A second matching workflow run is invalid. A GitHub rerun with
`run_attempt != 1` is invalid.

## Authority opened by DEC-448

Only:

`historical_result_slot_source_authorized = true`

is opened.

The following remain false:

- historical-result dispatch authorization;
- historical execution;
- historical result production;
- rerun;
- retry;
- replacement;
- reserved 2023-2026 robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Data boundary

Any later authorized historical run is still restricted to 2015-01-01 through
2022-12-31 already-seen design evidence.

The reserved robustness interval remains closed:

2023-01-01 through 2026-08-20.

## Next gate

The next decision may activate the exact DEC-447 runtime for this single slot and
provide an explicitly bounded one-shot dispatch path.

That later step must verify immediately before dispatch that:

- main still matches the authorized commit;
- no EXP-063 manual-main run already exists;
- run number 1 / attempt 1 remains available;
- the exact workflow, CLI, protocol, miner, evidence, adapter, and source blobs are
  unchanged.

DEC-448 itself provides no dispatch or execution path.
