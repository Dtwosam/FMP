# Phase 8A — EXP-061 Pre-Dispatch Governance

**Date:** 2026-09-27  
**Status:** GOVERNANCE SOURCE FROZEN / ZERO PRIOR RUNS OBSERVED / EXECUTION LOCKED  
**Decision:** DEC-277  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-276

## 1. Purpose

DEC-277 freezes the governance that must exist before any EXP-061 historical result run can be authorized.

It adds three independent protections:

1. a workflow-internal first-run guard;
2. a complete success/non-success terminal reviewer;
3. a read-only operator plan that never exposes a dispatch command.

DEC-277 does not authorize dispatch or execution.

## 2. Zero-prior-run observation

On 2026-09-27, before DEC-277 source was frozen, GitHub's manual-main workflow-run inventory was checked for:

- workflow name `phase8a-exp061-discovery`;
- workflow path `.github/workflows/phase8a-exp061-discovery.yml`;
- event `workflow_dispatch`;
- branch `main`.

Observed matching run count: **0**.

This observation does not itself authorize a run. A later authorization decision must recheck the live inventory.

## 3. Workflow-internal first-run guard

The active and reviewed workflow source now share successor blob:

`ca7dfccc1a11aeb49a91e5fb1d84519f08623538`.

Before EXP-044 source validation or historical execution, preflight fetches the workflow-specific manual-main run listing and calls:

`python scripts/phase8a_exp061.py guard-first-run`

The guard requires:

- exactly one relevant manual-main run exists at execution time;
- that one run is the current `GITHUB_RUN_ID`;
- its head is the current `GITHUB_SHA`;
- its run attempt is exactly 1;
- therefore there are zero prior manual-main EXP-061 runs.

Any prior run, second run, rerun attempt, path/name drift, or head mismatch fails closed.

The existing DEC-275 historical execution gate remains later in preflight and remains false.

## 4. Read-only operator plan

`build_read_only_operator_plan` classifies the workflow state without ever exposing a dispatch command.

When no run exists it reports:

`EXP061_READ_ONLY_AUTHORIZATION_GATE_REQUIRED`

and directs the project to freeze/merge a separate one-shot authorization decision.

When one run is in progress it reports:

`EXP061_RUN_IN_PROGRESS`

and forbids dispatch/retry/replacement.

When one run is terminal it reports:

`EXP061_TERMINAL_REVIEW_REQUIRED`

and routes the result through the frozen terminal reviewer.

More than one relevant manual-main run fails closed.

All dispatch/execution/downstream authorization flags remain false in every operator state.

## 5. Terminal review — successful run

A successful run must bind:

- exact workflow name/path;
- manual `main` event;
- attempt 1;
- terminal `success`;
- exactly the 20 DEC-274 job names;
- every one of those 20 jobs concluded `success`;
- exactly the 20 DEC-274 artifact names;
- every artifact is non-expired;
- exactly 18 independently valid DEC-272 cell-evidence objects;
- one independently valid DEC-274 aggregate evidence object.

The reviewer recomputes the aggregate evidence from the 18 validated cells using the run head as `code_commit` and requires exact semantic equality with the supplied aggregate.

A successful historical discovery run therefore still ends at:

`EXP061_HISTORICAL_RESULT_REVIEW_REQUIRED`

It does not authorize candidate compilation, reserved 2023-2026 access, promotion, shadow, demo, live, or trading.

## 6. Terminal review — non-success

Allowed non-success run conclusions are:

- `failure`;
- `cancelled`;
- `timed_out`.

The reviewer:

- validates the exact run identity and attempt;
- accepts only known DEC-274 job/artifact names;
- requires every supplied job to be terminal;
- preserves any valid partial cell evidence only as diagnostics;
- forbids aggregate evidence and aggregate artifact claims;
- records job/artifact counts;
- keeps rerun, retry, and replacement authorization false.

A non-success run ends at:

`EXP061_RUN_FAILURE_REVIEW_REQUIRED`.

## 7. CLI surface

The EXP-061 CLI now includes:

- `guard-first-run`;
- `operator-plan`;
- `terminal-review`.

The historical `cell` and `aggregate` commands remain behind the separate DEC-275 execution gate.

The operator-plan command emits no dispatch command.

## 8. Focused tests

Focused tests prove:

- zero-run inventory is recognized but not authorized;
- read-only operator plans contain no dispatch command;
- the first-run guard accepts only the current attempt-1 run;
- any prior/additional run fails closed;
- multiple runs fail operator planning;
- exact 20-job/20-artifact success plus 18 cells/aggregate reproduces;
- non-success never opens retry/replacement;
- missing success inventory fails closed.

## 9. Frozen implementation identities

- active and reviewed workflow blob: `ca7dfccc1a11aeb49a91e5fb1d84519f08623538`;
- governance source: `src/fmp/discovery/predispatch_governance.py`;
- governance blob: `1f8c0f6422041d621a9026f0983eabb967a8fa1c`;
- workflow-source validator blob: `6084fb6e482b65d6fd071f9a3ed58882ee991352`;
- workflow-install contract blob: `a052164daf13d19d7ac24c6d63a74f867744b6bd`;
- CLI blob: `7aebca5d2e64cc328b8400282cc522d9eaea5381`;
- focused governance tests: `tests/test_phase8a_exp061_predispatch_governance.py`;
- focused-test blob: `0f90e05655927e1540e3ce2e9f085f0f08ce1ef4`.

## 10. Authorization boundary

All remain false:

- workflow dispatch authorization;
- historical result-run authorization;
- historical discovery execution;
- discovery-result production;
- rerun/retry/replacement;
- reserved 2023-2026 access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## 11. Next gate

After DEC-277 merges green, the next safe step is a **separate one-shot authorization source** that:

1. rechecks zero prior manual-main runs on merged `main`;
2. binds the exact merged DEC-277 workflow/governance blobs;
3. changes only the historical-run execution authorization needed for one attempt;
4. retains the workflow-internal first-run guard and all rerun/retry/replacement locks;
5. still authorizes no reserved-block access, candidate compilation, promotion, demo, live, or trading.

No historical run may be dispatched until that separate authorization is merged and independently proven.
