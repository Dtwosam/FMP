# Phase 8A — EXP-015 Stage A First-Run Governance

**Date:** 2026-09-26
**Status:** SOURCE-ONLY FIRST-RUN GOVERNANCE / ONE BOUNDED SLOT OPEN / NOT DISPATCHED
**Decision:** DEC-264
**Experiment:** EXP-20260922-015
**Stage:** Stage A challenger discovery

## Purpose

DEC-264 modernizes execution governance for the already-frozen DEC-043/044 EXP-015 Stage A historical protocol without changing its research semantics.

This decision:

1. independently records the absence of any prior authoritative manual-main Stage A attempt;
2. preserves all 12 historical source-development push failures as immutable CI history;
3. adds a fail-closed first-run guard to the existing Stage A workflow;
4. predeclares exact attempt-1 terminal review;
5. opens at most one bounded authoritative Stage A historical-result slot;
6. does **not** dispatch that slot.

No strategy, parameter, pair, timeframe, date range, cost scenario, gate, ranking rule, survivor cap, data identity, or downstream acceptance rule changes.

## Bound predecessor

DEC-264 binds merged DEC-263 commit:

`46512e56abb097bd8e7f1a9503f762e3d18b3715`

DEC-263 established that:

- direct market-learning EXP-060 is closed with a credible negative result;
- Phase 8A remains active;
- EXP-015 Stage A/B/C is the unresolved historical branch;
- DEC-042 portfolio selection and DEC-045 Phase 8A acceptance remain blocked.

## Historical run audit

The public GitHub Actions history for `.github/workflows/phase8a-exp015-stage-a.yml` contains exactly 12 historical runs before DEC-264.

Every one of those runs is:

- event: `push`;
- branch: `phase8a/exp015-stage-a`;
- conclusion: `failure`;
- source-development CI, not an authoritative historical attempt.

The preserved run IDs are:

- `35718166743`
- `35718230009`
- `35718426118`
- `35718462124`
- `35718653498`
- `35718685088`
- `35718704592`
- `35718738298`
- `35718765257`
- `35718794889`
- `35718816153`
- `35718857036`

Before DEC-264 there are:

- authoritative Stage A `workflow_dispatch` runs from `main`: **0**;
- Stage B workflow runs: **0**;
- Stage C workflow runs: **0**.

DEC-264 does not delete, relabel, reinterpret, rerun, or replace any of the 12 development runs.

## Frozen Stage A research semantics

The existing DEC-043/044 Stage A research protocol remains unchanged:

- 567 immutable challenger identities;
- EURUSD, GBPUSD, USDJPY;
- 5m, 15m, 1h;
- six existing deterministic strategy families;
- Stage A range `2015-01-01` through `2018-12-31` inclusive;
- 0.2 / 0.5 / 1.0 pip scenarios;
- 0.2 and 0.5 pip gates remain mandatory;
- strict positive return and expectancy;
- profit factor strictly greater than 1.05;
- maximum drawdown at most 5%;
- at least 40 trades;
- at most two survivors per exact symbol/family/timeframe cell;
- 54 ranking cells;
- maximum 108 Stage A survivors;
- evidence remains `RETROSPECTIVE_ALREADY_SEEN`;
- `untouched_oos = false`;
- no lifecycle mutation or promotion.

Frozen source identities:

- challenger catalog source `src/fmp/portfolio/challenger_discovery.py`: blob `8b2a047668b6f607fee48dc09d7efb5fbdd153d7`;
- Stage A source `src/fmp/portfolio/challenger_discovery_stage_a.py`: blob `6f8be2a6d873b872ed8c47d5f3705a36c21958a5`;
- EXP-015 CLI `src/fmp/portfolio/exp015_cli.py`: blob `6d676dbc35bb0244d83dc3134893849022814a4a`;
- public script `scripts/phase8a_exp015.py`: blob `803ef9569880a6b22353e33b91ce63c9c9151424`.

## First-run guard

DEC-264 updates only the Stage A workflow execution boundary.

Guarded workflow:

`.github/workflows/phase8a-exp015-stage-a.yml`

Git blob:

`20ca8ec175a9a2405683bf239337c913625dfa33`

Before catalog freeze or data access, the workflow now requires the current run to be exactly:

- workflow name `phase8a-exp015-stage-a`;
- workflow path `.github/workflows/phase8a-exp015-stage-a.yml`;
- event `workflow_dispatch`;
- branch `main`;
- current `GITHUB_SHA`;
- exact current `main` head;
- `run_attempt == 1`.

It then lists only Stage A runs filtered to:

- branch `main`;
- event `workflow_dispatch`.

The current run ID is excluded from the prior-run set. Any prior authoritative manual-main Stage A attempt causes immediate failure before the historical computation opens.

The 12 old push-development failures are intentionally outside this authoritative attempt filter and remain preserved.

## Attempt-1 terminal review

Predeclared terminal-review source:

`src/fmp/portfolio/exp015_stage_a_terminal_review.py`

Git blob:

`502a7727d8f5302d2edd1d2473ea10da4cc223e0`

A successful authoritative Stage A attempt must have exactly 11 completed jobs:

- one `catalog-freeze`;
- nine `stage-a-cell (...)` matrix jobs;
- one `stage-a-authorize`.

Success requires all 11 jobs to succeed and all 11 expected non-expired artifacts:

- one frozen catalog artifact;
- nine exact symbol/timeframe Stage A artifacts;
- one Stage A authorization artifact.

The reviewer independently revalidates final authorization evidence against the result-producing head:

- exact protocol and experiment identity;
- retrospective label and `untouched_oos = false`;
- exact runner commit;
- exact catalog identity;
- exact six-strategy source digest;
- nine cells;
- 54 ranking cells;
- 567 strategy identities;
- maximum 108 survivors;
- survivor count/list consistency;
- exact nine cell identities;
- 63 strategies per cell;
- complete 567-strategy union;
- six family-ranking groups per cell;
- exact strategy-gate coverage;
- Stage B source-open flag equal only to whether survivors exist.

Even after successful Stage A review, `stage_b_execution_authorized = false`. A separate chronological gate must inspect the reviewed survivor evidence before Stage B can run.

For a terminal non-success:

- no retry is authorized;
- no replacement is authorized;
- no final Stage A authorization artifact may be claimed;
- only actually produced expected catalog/cell artifacts may be preserved;
- Stage B/C and all downstream gates remain locked.

## Authorization state

DEC-264 opens one bounded historical-result slot in the governance sense, but does not provide a dispatching operator or executor.

The following remain false:

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

No workflow is dispatched by DEC-264.

## Focused tests

`tests/test_phase8a_exp015_stage_a_first_run_governance.py`

Git blob:

`1ea17ac6329fa798c33c51b59c44ce437e0b739e`

The tests cover:

- exact workflow/event/branch/path/head/attempt first-run guard;
- absence of direct dispatch/rerun commands;
- deterministic validation of the exact 567-strategy Stage A authorization shape;
- rerun-attempt rejection;
- rejection of final authorization evidence on non-success;
- preservation of only expected partial artifacts on non-success;
- all downstream execution/trading locks remaining false.

## Next safe gate

After DEC-264 is green and merged, the next safe gate is a clean-main, one-way Stage A operator.

That operator may only classify the authoritative Stage A state as missing, in-progress, or terminal and produce the exact next action. It may not dispatch in its initial source-only decision.

A later repository-hosted read-only proof and separately reviewed one-shot executor are required before the single Stage A slot may be consumed.

Stage B/C, DEC-042, DEC-045, Phase 8B, demo, broker mutation, live orders, real-money action, and trading remain locked.
