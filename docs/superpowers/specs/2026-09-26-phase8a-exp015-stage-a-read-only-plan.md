# Phase 8A — EXP-015 Stage A Repository-Hosted Read-Only Plan Proof

**Date:** 2026-09-26
**Status:** SOURCE-ONLY / READ-ONLY / NOT DISPATCHED
**Decision:** DEC-266
**Experiment:** EXP-20260922-015
**Stage:** Stage A challenger discovery

## Purpose

DEC-266 adds a repository-hosted read-only proof for the exact DEC-265 EXP-015 Stage A `next` plan.

It exists only to prove, from merged `main`, that the single DEC-264 authoritative Stage A slot is still `MISSING` and that the frozen plan remains non-executing before any separate one-shot executor source is considered.

## Frozen predecessor binding

DEC-266 binds merged DEC-265 commit:

`ed4373a7a0da36850a5f08971e9e12bd63cf1554`

Frozen DEC-265 operator source:

`src/fmp/portfolio/exp015_stage_a_operator.py`

Git blob:

`3f2bca609ab6c1cd324f95c47be99584b11d9d90`

Frozen DEC-265 public CLI:

`scripts/phase8a_exp015_stage_a_operator.py`

Git blob:

`11010d32842b0f0ab829e0cc20d4654a7d5dcf2e`

Frozen DEC-264 Stage A workflow blob:

`ae8bdfbdb1bcfd62204a1bd0ec32dddfd9938930`

Frozen DEC-264 terminal-review blob:

`751c886f2d00e46d3c0a20fabbe0db4231db0d5d`

## Minimal proof runtime

Pinned proof requirements:

`requirements/exp015-stage-a-operator.txt`

Git blob:

`1ff32214dee10d877a067e750cd69ffad96d5fe5`

The proof runtime contains only the Polars packages required by the DEC-265 import chain:

- `polars==1.44.2`;
- `polars-runtime-32==1.44.2`.

The package is not installed editable. The proof uses `PYTHONPATH=src` and requires the checkout to remain clean after dependency installation.

## Read-only proof workflow

Workflow:

`.github/workflows/phase8a-exp015-stage-a-operator-plan.yml`

Git blob:

`be3a370dc538214d1758733c0b500ee3c7921609`

The workflow:

- runs only on pushes to `main` affecting the proof workflow or its frozen operator inputs;
- grants only `contents: read` and `actions: read`;
- has no `workflow_dispatch`, schedule, or pull-request trigger;
- checks out exact merged `main` with full history;
- requires local HEAD and `origin/main` to equal the triggering `GITHUB_SHA`;
- independently verifies the exact DEC-264 workflow/reviewer and DEC-265 operator/CLI Git blobs;
- requires merged DEC-265 commit `ed4373a7a0da36850a5f08971e9e12bd63cf1554` to be an ancestor of the triggering proof SHA;
- installs only the pinned proof runtime;
- requires a clean worktree after installation;
- invokes only `python scripts/phase8a_exp015_stage_a_operator.py next`;
- writes plan output only under `RUNNER_TEMP`;
- persists the read-only plan as an immutable artifact.

## Required proof result

A successful DEC-266 proof must report:

- `operator_decision = DEC-265`;
- `operator_read_only = true`;
- exact triggering `head_sha = GITHUB_SHA`;
- exact DEC-264 predecessor identities;
- no authoritative manual-main Stage A run;
- `run_state = MISSING`;
- no run id;
- stage `EXP015_STAGE_A_READ_ONLY_PROOF_REQUIRED`;
- `authoritative_slot_available = true`;
- `read_only_proof_required = true`;
- the exact future Stage A command as plan evidence only.

The planned command is:

`gh workflow run phase8a-exp015-stage-a.yml --ref main -R Dtwosam/FMP`

Every execution/downstream field must remain false, including Stage A dispatch, executor, retry, replacement, Stage B/C, DEC-042, DEC-045, Phase 8B, demo, broker mutation, live orders, real-money action, and trading.

## Prohibited actions

DEC-266 must not:

- invoke an `advance` path;
- invoke an `--execute` path;
- directly call `gh workflow run`;
- call a workflow dispatch REST endpoint;
- rerun or retry Stage A;
- create a replacement run;
- claim a Stage A result.

DEC-266 consumes no historical slot.

## Focused tests

Focused runner tests:

`tests/test_phase8a_exp015_stage_a_operator_plan_runner.py`

Git blob:

`8745125bec5ae27694ddb1e0c69ffc4ec865451b`

They pin main-push scope, read-only permissions, exact frozen source hashes, next-only execution, minimal pinned runtime, clean-worktree behavior, exact missing-slot plan shape, immutable plan persistence, and all downstream locks.

## Next gate

Only after this workflow succeeds on merged `main` and its exact non-expired plan artifact is independently bound may a separate one-shot executor source be considered.

DEC-266 itself dispatches nothing.
