# Phase 8A — EXP-057 One-Shot Operator Executor

**Date:** 2026-09-25
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE
**Decision:** DEC-228
**Experiment:** EXP-20260925-057

## Purpose

DEC-228 freezes exactly one repository-hosted executor for the already authorized DEC-225 first historical EXP-057 attempt.

The executor contains no independent model-workflow dispatch path. Its only execution-capable action is the frozen DEC-226 public operator:

`python scripts/phase8a_exp057_operator.py advance --execute`

## Frozen proof binding

DEC-228 binds the successful DEC-227 merged-main read-only proof:

- proof run id: `36192020278`
- proof head SHA: `7fc1396bbe983070dcbed410f43ce779f286986d`
- event: `push`
- branch: `main`
- attempt: `1`
- conclusion: `success`
- artifact id: `10888591924`
- artifact name: `exp057-dec226-read-only-operator-plan-7fc1396bbe983070dcbed410f43ce779f286986d`
- artifact digest: `sha256:92904a1e937494fcb065c414ac70fef9e4d4907bc86510d4bfaa98943982b9cf`
- artifact expired: `false`

The executor independently downloads the artifact ZIP, reproduces its SHA-256 digest, locates the single `operator-plan.json`, and revalidates the plan contents.

The plan must still show:

- `operator_decision = DEC-226`;
- clean merged main at the proof head;
- `read_only = true`;
- no existing EXP-057 model run;
- `run_state = MISSING`;
- exact repaired lower-tail dispatch-required stage;
- exact frozen dispatch command;
- the four bounded DEC-225 historical-run fields true;
- replacement/promotion/shadow/demo/broker/live/real-money/trading false.

## Executor workflow

Workflow:

`.github/workflows/phase8a-exp057-operator-execute.yml`

Git blob:

`600e428e4af0f13f56c69144e218bf5c998402a1`

The workflow:

- runs only on a push to `main` that adds or changes this exact executor workflow;
- grants `contents: read` and `actions: write`;
- checks out exact merged `main`;
- installs the pinned EXP-057 runtime without editable installation;
- requires the checkout to remain clean;
- revalidates the exact DEC-227 proof run, artifact metadata, ZIP digest, and plan contents;
- invokes only DEC-226 `advance --execute`;
- independently queries the exact EXP-057 model-workflow run listing after submission;
- requires exactly one manual-main EXP-057 run;
- requires the submitted run head SHA to equal the executor merge commit;
- requires attempt 1;
- persists executor evidence under runner temp.

The bounded run-list visibility loop only observes whether the submitted run has appeared in GitHub Actions. It does not rerun, retry, replace, or redispatch the model workflow.

## No independent dispatch path

DEC-228 contains no:

- direct `gh workflow run phase8a-exp057-...` command;
- workflow-dispatch REST POST;
- GitHub rerun command;
- model-run retry;
- replacement dispatch path.

DEC-226 remains solely responsible for the one permitted dispatch decision and performs fresh clean-main/live-state double planning immediately before execution.

## Focused tests

Focused executor tests:

`tests/test_phase8a_exp057_operator_executor.py`

Git blob:

`b526852eff3254bbd54c6afc43cb62f8f7c706a8`

They pin one-push scope, DEC-226-only execution, exact DEC-227 proof identities, ZIP digest/content validation, clean checkout behavior, independent single-run confirmation, and evidence persistence outside the checkout.

## One-attempt semantics

If the initial merged-main executor causes DEC-226 to submit the guarded EXP-057 workflow, that first manual-main run consumes the DEC-225 slot on any terminal outcome.

No second executor attempt, model rerun, retry, or replacement is authorized.

Any terminal model-run outcome must route through DEC-224.

## Downstream locks

DEC-228 does not authorize:

- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.
