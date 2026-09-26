# Phase 8A — EXP-058 One-Shot Operator Executor

**Date:** 2026-09-26
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE
**Decision:** DEC-239
**Experiment:** EXP-20260925-058

## Purpose

DEC-239 freezes exactly one repository-hosted executor for the already authorized DEC-236 first historical EXP-058 attempt.

The executor contains no independent model-workflow dispatch path. Its only execution-capable action is the frozen DEC-237 public operator:

`python scripts/phase8a_exp058_operator.py advance --execute`

## Frozen proof binding

DEC-239 binds the successful DEC-238 merged-main read-only proof:

- proof run id: `36206173161`
- proof head SHA: `c25efaff4a0bb9ad4c8e3b51eee55da0f7991d0e`
- event: `push`
- branch: `main`
- attempt: `1`
- conclusion: `success`
- artifact id: `10894115135`
- artifact name: `exp058-dec237-read-only-operator-plan-c25efaff4a0bb9ad4c8e3b51eee55da0f7991d0e`
- artifact digest: `sha256:5f75874e78a04db86f6f839a08a1fec581e9854ca26c4f363459dba5ffa69857`
- artifact expired: `false`

The executor independently downloads the artifact ZIP, reproduces its SHA-256 digest, locates the single `operator-plan.json`, and revalidates the plan contents.

The plan must still show:

- `operator_decision = DEC-237`;
- clean merged main at the proof head;
- `read_only = true`;
- no existing EXP-058 model run;
- `run_state = MISSING`;
- exact residual-regime-floor dispatch-required stage;
- exact frozen dispatch command;
- the four bounded DEC-236 historical-run fields true;
- replacement/promotion/shadow/demo/broker/live/real-money/trading false.

## Executor workflow

Workflow:

`.github/workflows/phase8a-exp058-operator-execute.yml`

Git blob:

`5241ea0b4d8b23dff3ef0f190240bb08d248218c`

The workflow:

- runs only on a push to `main` that adds or changes this exact executor workflow;
- has `contents: read` and `actions: write`;
- checks out exact merged `main`;
- installs the pinned EXP-058 runtime without editable installation;
- requires the checkout to remain clean;
- revalidates the exact DEC-238 proof run, artifact metadata, ZIP digest, and plan contents;
- invokes only DEC-237 `advance --execute`;
- independently queries the exact EXP-058 model-workflow run listing after submission;
- requires exactly one manual-main EXP-058 run;
- requires the submitted run head SHA to equal the executor merge commit;
- requires attempt 1;
- persists executor evidence under runner temp.

The bounded run-list visibility loop only observes whether the submitted run has appeared in GitHub Actions. It does not rerun, retry, replace, or redispatch the model workflow.

## No independent dispatch path

DEC-239 contains no:

- direct `gh workflow run phase8a-exp058-...` command;
- workflow-dispatch REST POST;
- GitHub rerun command;
- model-run retry;
- replacement dispatch path.

DEC-237 remains solely responsible for the one permitted dispatch decision and performs fresh clean-main/live-state double planning immediately before execution.

## Focused tests

Focused executor tests:

`tests/test_phase8a_exp058_operator_executor.py`

Git blob:

`5fc16bec72a7dd04d2bf3380c85213cbe3ffd7c6`

They pin one-push scope, DEC-237-only execution, exact DEC-238 proof identities, ZIP digest/content validation, clean checkout behavior, independent single-run confirmation, and evidence persistence outside the checkout.

## One-attempt semantics

If the initial merged-main executor causes DEC-237 to submit the guarded EXP-058 workflow, that first manual-main run consumes the DEC-236 slot on any terminal outcome.

No second executor attempt, model rerun, retry, or replacement is authorized.

Any terminal model-run outcome must route through DEC-235.

## Downstream locks

DEC-239 does not authorize:

- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.
