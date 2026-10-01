# Phase 8A — EXP-064 One-Shot Historical Slot Authorization

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY ONE-SHOT SLOT AUTHORIZATION / DISPATCH LOCKED  
**Decision:** DEC-456  
**Experiment:** EXP-20261001-064  
**Predecessor:** DEC-455

## Purpose

DEC-456 opens exactly one source-authorized EXP-064 historical-result slot while
keeping workflow dispatch, historical execution, and result production locked.

It does not dispatch the workflow and does not change the DEC-455 runtime gate.

## Bound runtime

DEC-456 binds merged DEC-455 commit:

`c388def44d251c96832572f07de43d9dc6a909ee`

and exact blobs:

- DEC-455 runtime source:
  `07e5ccebb6416c04621aa54e170cd4eb1e0a2a04`;
- active EXP-064 workflow:
  `caca62672ad9796764c18be6b8da9785b98c9733`;
- locked EXP-064 CLI:
  `a44aed6d890e25a781b7b92d7efb3dabe06f9047`;
- DEC-454 evidence contract:
  `9aee3f9e273e20329c9de5a7079ed924ffee0a9a`;
- DEC-453 continuous-stability miner:
  `b0d799ec1afaf43b0441290c97a9f39c37ecd2fd`;
- DEC-452 continuous-stability protocol:
  `c108ea047c7bfbac33993180066c28ad`.

Authorization source:

`src/fmp/discovery/exp064_historical_run_authorization.py`

blob:

`0668910a69a87fad06be73af98e5f403436fe7fb`

Focused tests:

`tests/test_phase8a_exp064_historical_run_authorization.py`

blob:

`08f9181bc0fd8d70959c7f1e595dda43ce96ccf7`

## Current run inventory

At DEC-456 creation time, the installed
`phase8a-exp064-continuous-stability` workflow has zero matching manual-main
`workflow_dispatch` runs.

The workflow was installed by DEC-455 immediately before this decision. The
repository's post-install run inventory contains no run with the exact EXP-064
workflow name, path, event, and main branch identity.

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

- workflow: `phase8a-exp064-continuous-stability`;
- path: `.github/workflows/phase8a-exp064-continuous-stability.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- run number: 1;
- run attempt: 1.

A second matching workflow run is invalid. A GitHub rerun with
`run_attempt != 1` is invalid.

## Authority opened by DEC-456

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

Any later authorized historical run remains restricted to already-seen design
evidence from 2015-01-01 through 2022-12-31.

The reserved robustness interval remains closed:

2023-01-01 through 2026-08-20.

## Next gate

The next decision may activate the exact DEC-455 runtime for this single slot and
provide an explicitly bounded one-shot dispatch path.

That later step must verify immediately before dispatch that:

- main still matches the authorized activation commit;
- no EXP-064 manual-main run already exists;
- run number 1 / attempt 1 remains available;
- the exact workflow, CLI, protocol, miner, evidence, adapter, loader, and source
  blobs are unchanged.

DEC-456 itself provides no dispatch or execution path.
