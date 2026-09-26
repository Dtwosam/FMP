# Phase 8A — EXP-015 Stage A Clean-Main One-Way Operator

**Date:** 2026-09-26
**Status:** SOURCE-ONLY / READ-ONLY / NOT DISPATCHED
**Decision:** DEC-265
**Experiment:** EXP-20260922-015
**Stage:** Stage A challenger discovery

## Purpose

DEC-265 freezes a clean-main, fail-closed operator for the single bounded DEC-264 EXP-015 Stage A historical-result slot.

It does not dispatch Stage A and cannot consume the slot. It only classifies the exact authoritative manual-main workflow state and returns the one next action.

## Frozen predecessor binding

DEC-265 binds merged DEC-264 commit:

`92ef2668b1a0cb416e7f772a8a061d2f280005a1`

Frozen DEC-264 Stage A workflow blob:

`ae8bdfbdb1bcfd62204a1bd0ec32dddfd9938930`

Frozen DEC-264 terminal-review blob:

`751c886f2d00e46d3c0a20fabbe0db4231db0d5d`

The DEC-043/044 research protocol remains unchanged.

## Clean-main preflight

Before live-state classification, the operator requires:

- local branch exactly `main`;
- local HEAD exactly equal to freshly fetched `origin/main`;
- clean working tree;
- origin remote exactly `Dtwosam/FMP`.

Any mismatch fails closed.

## Authoritative run selection

The operator queries only:

`phase8a-exp015-stage-a.yml`

filtered to:

- branch `main`;
- event `workflow_dispatch`.

The 12 preserved historical `push` failures on `phase8a/exp015-stage-a` remain outside the authoritative slot.

More than one authoritative manual-main Stage A run is rejected as a DEC-264 violation. A selected run must have the exact workflow name/path, a valid 40-character head SHA, and `run_attempt == 1`.

## One-way live state

The authoritative Stage A state is classified as exactly one of:

- `MISSING`;
- `IN_PROGRESS`;
- `TERMINAL`.

For `MISSING`, the operator reports:

- one bounded authoritative slot is still available;
- a repository-hosted read-only proof is required next;
- the exact future dispatch command as plan evidence only.

The frozen planned command is:

`gh workflow run phase8a-exp015-stage-a.yml --ref main -R Dtwosam/FMP`

DEC-265 does not authorize or submit that command.

For `IN_PROGRESS`, no dispatch plan is exposed. The existing run is the only authoritative attempt and must be inspected without rerun, retry, or replacement.

For `TERMINAL`, no dispatch plan is exposed. The run must be validated through the frozen DEC-264 terminal-review contract, again with no rerun, retry, or replacement.

## Locked authority

Every DEC-265 report keeps the following false:

- Stage A dispatch authorization;
- Stage A executor authorization;
- Stage A retry authorization;
- Stage A replacement authorization;
- Stage B execution authorization;
- Stage C execution authorization;
- DEC-042 portfolio selection authorization;
- DEC-045 Phase 8A acceptance authorization;
- Phase 8B authorization;
- demo-order authorization;
- broker mutation authorization;
- live-order authorization;
- real-money authorization;
- trading authorization.

The report validator independently fails closed if any of these fields are loosened.

## Operator source

Operator source:

`src/fmp/portfolio/exp015_stage_a_operator.py`

Git blob:

`f385b764581e8dd45b683e275233245082945e7a`

Public CLI:

`scripts/phase8a_exp015_stage_a_operator.py`

Git blob:

`11010d32842b0f0ab829e0cc20d4654a7d5dcf2e`

The CLI exposes only:

`next`

There is no `advance`, `--execute`, direct workflow-dispatch endpoint, rerun path, or replacement path.

## Focused tests

Focused tests:

`tests/test_phase8a_exp015_stage_a_operator.py`

Git blob:

`b297aed894f2b29ccb4070f7c0105b7cd3a7bafe`

They pin:

- exact DEC-264 predecessor identities;
- clean-main checkout rules;
- exact manual-main Stage A endpoint;
- preservation of old push-run history outside the authoritative slot;
- one-run-only and attempt-1 selection;
- one-way `MISSING / IN_PROGRESS / TERMINAL` classification;
- plan-only dispatch evidence for `MISSING`;
- no dispatch plan after the slot is used;
- all downstream locks;
- tamper rejection;
- `next`-only public CLI behavior.

## Next gate

After DEC-265 is green and merged, the next safe gate is a repository-hosted read-only proof of the exact `next` plan on merged `main`.

That proof must have read-only permissions, must not call Stage A dispatch directly or indirectly, and must persist the exact plan as immutable evidence.

Only after that proof succeeds may a separately reviewed one-shot executor source be considered.

DEC-265 itself dispatches nothing.
