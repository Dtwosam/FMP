# Phase 8A — EXP-015 Stage A One-Shot Executor

**Date:** 2026-09-26
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE
**Decision:** DEC-267
**Experiment:** EXP-20260922-015
**Stage:** Stage A challenger discovery

## Purpose

DEC-267 freezes exactly one repository-hosted executor for the sole DEC-264 EXP-015 Stage A authoritative historical-result slot.

It does not alter the DEC-043/044 research protocol. It exists only to consume the already-governed Stage A slot once, after the successful DEC-266 merged-main read-only proof.

## Frozen DEC-266 proof binding

DEC-267 binds the successful merged-main DEC-266 proof:

- proof run id: `36277672941`;
- proof workflow: `phase8a-exp015-stage-a-operator-plan`;
- proof workflow path: `.github/workflows/phase8a-exp015-stage-a-operator-plan.yml`;
- proof head SHA: `82a90af8edbf156e89df3a63f2003da71d4473d3`;
- event: `push`;
- branch: `main`;
- attempt: `1`;
- conclusion: `success`;
- artifact id: `10917841059`;
- artifact name: `exp015-dec265-stage-a-read-only-plan-82a90af8edbf156e89df3a63f2003da71d4473d3`;
- artifact digest: `sha256:b5cc74574518bc0db4a9229e1b55117fa99ec2b17264f7ee42a538df0adc3cf3`;
- artifact expired: `false`.

The executor independently revalidates the exact proof run metadata, artifact metadata, ZIP SHA-256 digest, and the single `operator-plan.json`.

The plan must show DEC-265, read-only mode, exact proof head, clean verified main, no existing authoritative Stage A run, `MISSING` state, the sole slot still available, the exact planned Stage A command, and every execution/downstream field still false.

## Fresh execution validator

Source:

`src/fmp/portfolio/exp015_stage_a_executor.py`

Git blob:

`840659456732b21cae1520060ab0539c9636066c`

The validator reuses the frozen DEC-265 report validator, then additionally requires:

- `operator_decision = DEC-265`;
- executor-plan head exactly equal to the executor `GITHUB_SHA`;
- `run_present = false`;
- `run_state = MISSING`;
- no run id;
- stage `EXP015_STAGE_A_READ_ONLY_PROOF_REQUIRED`;
- the sole authoritative slot still available;
- read-only proof shape still present;
- the exact frozen Stage A dispatch tuple from DEC-265.

Any identity, slot, state, stage, command, retry, replacement, or downstream-lock tamper fails closed.

## Executor CLI

Public executor:

`scripts/phase8a_exp015_stage_a_executor.py`

Git blob:

`201609db2d7ed2796dd492d97a75bdee57bcc0ee`

The CLI:

- requires a `push` on `refs/heads/main`;
- requires `GITHUB_RUN_ATTEMPT == 1`;
- requires a valid executor `GITHUB_SHA`;
- invokes the DEC-265 public `next` planner twice immediately before submission;
- requires the two fresh plans to be byte-for-byte equivalent as parsed JSON;
- independently validates both plans against the executor head;
- requires both plans to return the exact same frozen dispatch tuple;
- executes only that tuple;
- emits immutable evidence marking `fresh_plan_rechecked_twice = true`, `dispatch_submitted = true`, and `result_claimed = false`.

The executor script contains no independent Stage A workflow-dispatch string, REST dispatch endpoint, rerun command, retry path, or replacement path.

## One-shot workflow

Workflow:

`.github/workflows/phase8a-exp015-stage-a-operator-execute.yml`

Git blob:

`fd7c45bb6f47dcb5d441312bb58981589a7f1850`

The workflow:

- runs only on a push to `main` changing the executor workflow, CLI, or validator;
- grants only `contents: read` and `actions: write`;
- checks out full-history `main`;
- requires local HEAD and `origin/main` to equal the exact triggering `GITHUB_SHA`;
- requires executor `run_attempt == 1`;
- requires the DEC-266 merge commit to be an ancestor of the executor head;
- re-hashes and pins the DEC-264 guarded Stage A workflow, DEC-264 terminal reviewer, DEC-265 operator, DEC-265 public CLI, and pinned EXP-015 operator runtime before any GitHub write is possible;
- queries its own workflow history and rejects any prior different main/push executor run;
- installs only the pinned EXP-015 operator runtime from `requirements/exp015-stage-a-operator.txt` at blob `1ff32214dee10d877a067e750cd69ffad96d5fe5`;
- requires the checkout to remain clean;
- revalidates the exact DEC-266 run, artifact, digest, and plan contents;
- independently queries the Stage A manual-main run listing immediately before execution and requires it to be empty;
- invokes only `python scripts/phase8a_exp015_stage_a_executor.py`;
- after submission, polls only for run visibility and requires exactly one Stage A manual-main run;
- requires that run to have exact workflow name/path, executor merge head, and `run_attempt == 1`;
- stores executor evidence only under runner temp and uploads it immutably.

The bounded visibility loop cannot dispatch, rerun, retry, or replace Stage A.

## Focused tests

Fresh-plan validator and CLI tests:

`tests/test_phase8a_exp015_stage_a_executor.py`

Git blob:

`0b352ce29753ed747cd6fed9f98dbac2a95172e6`

Workflow tests:

`tests/test_phase8a_exp015_stage_a_operator_executor.py`

Git blob:

`c58ad493ef3914882e5d3106a5f91f83d056c0f7`

They pin exact proof identities, first-executor semantics, exact-trigger SHA binding, no prior executor run, pre-dispatch empty-slot proof, double fresh planning, no direct workflow-dispatch path in the workflow, exactly-one submitted Stage A observation, no rerun/replacement path, and evidence persistence outside the checkout.

## One-attempt semantics

If the merged-main executor submits Stage A, that first authoritative manual-main Stage A run consumes the DEC-264 slot regardless of terminal outcome.

No second executor run, Stage A rerun, retry, or replacement is authorized.

Any terminal Stage A result must route through the frozen DEC-264 terminal-review contract.

## Downstream locks

DEC-267 does not authorize Stage B, Stage C, portfolio selection, Phase 8A acceptance, Phase 8B, demo orders, broker mutation, live orders, real-money action, or trading.
