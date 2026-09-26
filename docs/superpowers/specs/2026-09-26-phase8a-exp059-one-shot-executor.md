# Phase 8A — EXP-059 One-Shot Operator Executor

**Date:** 2026-09-26
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE
**Decision:** DEC-250
**Experiment:** EXP-20260926-059

## Purpose

DEC-250 freezes exactly one repository-hosted executor for the already authorized DEC-247 first historical EXP-059 attempt.

The executor contains no independent model-workflow dispatch path. Its only execution-capable action is the frozen DEC-248 public operator:

`python scripts/phase8a_exp059_operator.py advance --execute`

## Frozen proof binding

DEC-250 binds successful DEC-249 merged-main read-only proof:

- proof run id: `36238966706`
- proof head SHA: `adb5e127b92feedff2653a1b9ba24de4621246da`
- event: `push`
- branch: `main`
- attempt: `1`
- conclusion: `success`
- artifact id: `10904883676`
- artifact name: `exp059-dec248-read-only-operator-plan-adb5e127b92feedff2653a1b9ba24de4621246da`
- artifact digest: `sha256:3fba24ae0101e20c5c98751134b956076fc3d0ecb38af25f59377802c7b2d6d4`
- artifact expired: `false`

The executor independently revalidates the proof run metadata, artifact metadata, ZIP SHA-256 digest, and the single `operator-plan.json`.

The plan must still show:

- `operator_decision = DEC-248`;
- clean merged main at the proof head;
- `read_only = true`;
- no existing EXP-059 model run;
- `run_state = MISSING`;
- exact regime-balance dispatch-required stage;
- exact frozen dispatch command;
- the four bounded DEC-247 historical-run fields true;
- replacement/promotion/shadow/demo/broker/live/real-money/trading false.

## Executor workflow

Workflow:

`.github/workflows/phase8a-exp059-operator-execute.yml`

Git blob:

`d207314d107e30ead9b5f77582bf8a7990625067`

The workflow:

- runs only on a push to `main` that adds or changes this exact executor workflow;
- grants `contents: read` and `actions: write`;
- checks out exact merged `main`;
- installs the pinned EXP-059 runtime without editable installation;
- requires the checkout to remain clean;
- revalidates the exact DEC-249 proof run, artifact metadata, ZIP digest, and plan contents;
- invokes only DEC-248 `advance --execute`;
- independently queries the exact EXP-059 model-workflow run listing after submission;
- requires exactly one manual-main EXP-059 run;
- requires the submitted run head SHA to equal the executor merge commit;
- requires attempt 1;
- persists executor evidence under runner temp.

The bounded run-list visibility loop only observes whether the submitted run has appeared in GitHub Actions. It does not rerun, retry, replace, or redispatch the model workflow.

## No independent dispatch path

DEC-250 contains no:

- direct `gh workflow run phase8a-exp059-...` command;
- workflow-dispatch REST POST;
- GitHub rerun command;
- model-run retry;
- replacement dispatch path.

DEC-248 remains solely responsible for the one permitted dispatch decision and performs fresh clean-main/live-state double planning immediately before execution.

## Focused tests

Focused executor tests:

`tests/test_phase8a_exp059_operator_executor.py`

Git blob:

`f9da2b1e1e5bfb1fbc2f260dc98b7d5da18104c6`

They pin one-push scope, DEC-248-only execution, exact DEC-249 proof identities, ZIP digest/content validation, clean checkout behavior, independent single-run confirmation, and evidence persistence outside the checkout.

## One-attempt semantics

If the initial merged-main executor causes DEC-248 to submit the guarded EXP-059 workflow, that first manual-main run consumes the DEC-247 slot on any terminal outcome.

No second executor attempt, model rerun, retry, or replacement is authorized.

Any terminal model-run outcome must route through DEC-246.

## Downstream locks

DEC-250 does not authorize:

- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.
