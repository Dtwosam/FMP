# Phase 8A — EXP-060 One-Shot Operator Executor

**Date:** 2026-09-26
**Status:** APPROVED SOURCE; AUTOMATIC EXECUTION ONLY AFTER MERGE
**Decision:** DEC-261
**Experiment:** EXP-20260926-060

## Purpose

DEC-261 freezes exactly one repository-hosted executor for the already authorized DEC-258 first historical EXP-060 attempt.

The executor contains no independent model-workflow dispatch path. Its only execution-capable action is the frozen DEC-259 public operator:

`python scripts/phase8a_exp060_operator.py advance --execute`

## Frozen proof binding

DEC-261 binds successful DEC-260 merged-main read-only proof:

- proof run id: `36258921030`
- proof head SHA: `0339c58f59206b6e70fb5019be403ee9ffdd1a34`
- event: `push`
- branch: `main`
- attempt: `1`
- conclusion: `success`
- artifact id: `10911029039`
- artifact name: `exp060-dec248-read-only-operator-plan-0339c58f59206b6e70fb5019be403ee9ffdd1a34`
- artifact digest: `sha256:b51e691984368757138913d646c4561150b02e6afd437773a3758e5559f3748f`
- artifact expired: `false`

The executor independently revalidates the proof run metadata, artifact metadata, ZIP SHA-256 digest, and the single `operator-plan.json`.

The plan must still show:

- `operator_decision = DEC-259`;
- clean merged main at the proof head;
- `read_only = true`;
- no existing EXP-060 model run;
- `run_state = MISSING`;
- exact regime-balance dispatch-required stage;
- exact frozen dispatch command;
- the four bounded DEC-258 historical-run fields true;
- replacement/promotion/shadow/demo/broker/live/real-money/trading false.

## Executor workflow

Workflow:

`.github/workflows/phase8a-exp060-operator-execute.yml`

Git blob:

`e614736b287655c6b529799e2b5aaec052dd8c52`

The workflow:

- runs only on a push to `main` that adds or changes this exact executor workflow;
- grants `contents: read` and `actions: write`;
- checks out exact merged `main`;
- installs the pinned EXP-060 runtime without editable installation;
- requires the checkout to remain clean;
- revalidates the exact DEC-260 proof run, artifact metadata, ZIP digest, and plan contents;
- invokes only DEC-259 `advance --execute`;
- independently queries the exact EXP-060 model-workflow run listing after submission;
- requires exactly one manual-main EXP-060 run;
- requires the submitted run head SHA to equal the executor merge commit;
- requires attempt 1;
- persists executor evidence under runner temp.

The bounded run-list visibility loop only observes whether the submitted run has appeared in GitHub Actions. It does not rerun, retry, replace, or redispatch the model workflow.

## No independent dispatch path

DEC-261 contains no:

- direct `gh workflow run phase8a-exp060-...` command;
- workflow-dispatch REST POST;
- GitHub rerun command;
- model-run retry;
- replacement dispatch path.

DEC-259 remains solely responsible for the one permitted dispatch decision and performs fresh clean-main/live-state double planning immediately before execution.

## Focused tests

Focused executor tests:

`tests/test_phase8a_exp060_operator_executor.py`

Git blob:

`0e601be70e0cf2c7ac15355e969f2f50226c3c9f`

They pin one-push scope, DEC-259-only execution, exact DEC-260 proof identities, ZIP digest/content validation, clean checkout behavior, independent single-run confirmation, and evidence persistence outside the checkout.

## One-attempt semantics

If the initial merged-main executor causes DEC-259 to submit the guarded EXP-060 workflow, that first manual-main run consumes the DEC-258 slot on any terminal outcome.

No second executor attempt, model rerun, retry, or replacement is authorized.

Any terminal model-run outcome must route through DEC-257.

## Downstream locks

DEC-261 does not authorize:

- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.
