# Phase 8A — EXP-056 One-Shot Operator Executor

**Date:** 2026-09-25
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE
**Decision:** DEC-217
**Experiment:** EXP-20260925-056

## Purpose

DEC-217 freezes exactly one repository-hosted executor for the already authorized DEC-214 first historical EXP-056 attempt.

The executor does not contain an independent model-workflow dispatch path. Its only execution-capable action is the frozen DEC-215 public operator:

`python scripts/phase8a_exp056_operator.py advance --execute`

## Frozen proof binding

DEC-217 binds the successful DEC-216 merged-main read-only proof:

- proof run id: `36175134738`
- proof head SHA: `8345129a80822f91f42681846f5f3a0eb63c8218`
- event: `push`
- branch: `main`
- attempt: `1`
- conclusion: `success`
- artifact id: `10882710327`
- artifact name: `exp056-dec215-read-only-operator-plan-8345129a80822f91f42681846f5f3a0eb63c8218`
- artifact digest: `sha256:dfbf6ffc5c2201e2f4a6f7e6118048d416ca6cc9f56e78cde36fae7361ccc9d3`
- artifact expired: `false`

The executor independently downloads the artifact ZIP, reproduces its SHA-256 digest, locates the single `operator-plan.json`, and revalidates the plan contents.

The plan must still show:

- `operator_decision = DEC-215`;
- clean merged main at the proof head;
- `read_only = true`;
- no existing EXP-056 model run;
- `run_state = MISSING`;
- exact lower-tail dispatch-required stage;
- exact frozen dispatch command;
- the four bounded DEC-214 historical-run fields true;
- replacement/promotion/shadow/demo/broker/live/real-money/trading false.

## Executor workflow

Workflow:

`.github/workflows/phase8a-exp056-operator-execute.yml`

Git blob:

`4c3d34059692b646d36f41d1353edf8e58e662ca`

The workflow:

- runs only on a push to `main` that adds or changes this exact executor workflow;
- has `contents: read` and `actions: write`;
- checks out exact merged `main`;
- installs the pinned EXP-056 runtime without editable installation;
- requires the checkout to remain clean;
- revalidates the exact DEC-216 proof run, artifact metadata, ZIP digest, and plan contents;
- invokes only DEC-215 `advance --execute`;
- independently queries the exact EXP-056 model-workflow run listing after submission;
- requires exactly one manual-main EXP-056 run;
- requires the submitted run head SHA to equal the executor merge commit;
- requires attempt 1;
- persists executor evidence under runner temp.

The short bounded run-list visibility loop only observes whether the submitted run has appeared in GitHub Actions. It does not rerun, retry, replace, or redispatch the model workflow.

## No independent dispatch path

DEC-217 contains no:

- direct `gh workflow run phase8a-exp056-...` command;
- workflow-dispatch REST POST;
- GitHub rerun command;
- model-run retry;
- replacement dispatch path.

DEC-215 remains solely responsible for the one permitted dispatch decision and performs fresh clean-main/live-state double planning immediately before execution.

## Focused tests

Focused executor tests:

`tests/test_phase8a_exp056_operator_executor.py`

Git blob:

`10a4cd1355fc9ee068ea32097b3f3aa7ea6fc2ef`

They pin one-push scope, DEC-215-only execution, exact DEC-216 proof identities, ZIP digest/content validation, clean checkout behavior, independent single-run confirmation, and evidence persistence outside the checkout.

## One-attempt semantics

If the initial merged-main executor causes DEC-215 to submit the guarded EXP-056 workflow, that first manual-main run consumes the DEC-214 slot on any terminal outcome.

No second executor attempt, model rerun, retry, or replacement is authorized.

Any terminal model-run outcome must route through DEC-213.

## Downstream locks

DEC-217 does not authorize:

- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

