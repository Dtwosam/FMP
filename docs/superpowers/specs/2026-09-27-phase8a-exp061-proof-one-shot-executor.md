# Phase 8A — EXP-061 One-Shot Proof-Only Executor

**Date:** 2026-09-27  
**Status:** APPROVED SOURCE / ONE PROOF DISPATCH AFTER MERGE ONLY  
**Decision:** DEC-279  
**Experiment:** EXP-20260927-061  
**Predecessors:** DEC-276, DEC-277, DEC-278

## 1. Purpose

DEC-279 authorizes exactly one **proof-only** dispatch of the installed EXP-061 workflow after this decision merges to `main`.

The proof is expected to fail at the locked DEC-275 execution gate. It is not a historical discovery run and it does not consume the future historical-result slot.

## 2. Exact proof target

The only allowed target is:

- workflow: `phase8a-exp061-discovery`;
- path: `.github/workflows/phase8a-exp061-discovery.yml`;
- event: `workflow_dispatch`;
- ref: `main`;
- run attempt: `1`;
- target head: the exact DEC-279 merged-main `GITHUB_SHA`.

The target workflow remains byte-pinned to blob:

`d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`.

That workflow still calls `require-execution` before any cell work, and historical execution authorization remains false.

## 3. Fresh-plan requirement

Immediately before the one proof dispatch, the executor invokes the DEC-278 read-only planner twice against live GitHub metadata.

Both plans must be identical and must show:

- current `main` equals the executor `GITHUB_SHA`;
- zero matching manual-main EXP-061 runs;
- stage `EXP061_PROOF_DISPATCH_AUTHORIZATION_REQUIRED`;
- no run id;
- exact planned command `gh workflow run phase8a-exp061-discovery.yml --ref main`;
- DEC-278 proof dispatch authorization still false;
- DEC-278 execute mode still unavailable;
- historical-result dispatch false;
- historical discovery execution false;
- discovery-result authorization false;
- trading false.

DEC-279, not DEC-278, supplies the single narrow proof-dispatch authorization.

## 4. Executor validator

Source:

`src/fmp/discovery/proof_executor.py`

Blob:

`0558b5d6b5db41e252cfb0e1cc3bc46ef489b0d0`

The validator accepts only the exact fresh DEC-278 missing-run shape and returns only the frozen proof dispatch tuple.

It rejects:

- any existing proof run;
- head drift;
- operator/version drift;
- any non-missing stage;
- any proof run id;
- any non-zero matching-run count;
- any historical/result/trading authority drift;
- any command drift.

## 5. Executor CLI

CLI:

`scripts/phase8a_exp061_proof_executor.py`

Blob:

`db3fdb6d283ce33a71a6dd57eebfef70874fd40a`

The CLI:

- requires a `push` on `refs/heads/main`;
- requires `GITHUB_RUN_ATTEMPT == 1`;
- requires repository `Dtwosam/FMP`;
- reads live `main` and target-workflow run metadata;
- builds and validates the fresh proof plan twice;
- requires the two parsed plans and dispatch tuples to be identical;
- submits only the frozen proof command;
- emits evidence marking proof dispatch submitted;
- explicitly records historical-result slot consumed = false and historical-result claimed = false.

The CLI contains no discovery-cell/aggregate execution command and no retry/rerun/replacement mode.

## 6. One-shot workflow

Workflow:

`.github/workflows/phase8a-exp061-proof-one-shot-execute.yml`

Blob:

`7e9b31d3dc521b05ed5dedaafa57afef57222ef2`

The workflow runs only on the first qualifying push to `main` changing the DEC-279 executor surface.

It grants:

- `contents: read`;
- `actions: write`.

Before any GitHub write it requires:

- exact push/main/attempt-1 identity;
- local HEAD and `origin/main` equal `GITHUB_SHA`;
- exact repository identity;
- exact target workflow blob;
- exact DEC-275 workflow-source blob;
- exact DEC-277 proof-contract blob;
- exact DEC-278 operator and CLI blobs;
- exact DEC-279 validator and CLI blobs;
- exact pinned runtime requirements;
- no earlier DEC-279 executor run;
- clean worktree;
- zero existing target proof runs.

After submission it only polls for visibility and requires exactly one target manual-main proof run with the DEC-279 merge head and attempt 1.

It does not wait for or interpret the terminal proof result. That belongs to DEC-277/DEC-280 review.

## 7. Focused tests

Focused tests:

`tests/test_phase8a_exp061_proof_executor.py`

Blob:

`a331da912f06cd9f34ba510c1e86ba726ab6c0fd`

They cover:

- valid fresh proof-only plan;
- existing-run refusal;
- head-drift refusal;
- tampered DEC-278 read-only authority refusal;
- proof-only authorization with every historical/result/retry/trading authority false;
- absence of direct discovery-cell/aggregate commands;
- exact target workflow and DEC-278 source pins.

## 8. One-shot semantics

If DEC-279 merges and its executor submits the proof:

- exactly one manual-main EXP-061 proof run may exist;
- no second proof dispatch is authorized;
- executor reruns are refused;
- historical-result slot remains unconsumed;
- historical discovery execution remains unauthorized.

The proof is expected to fail at the execution gate and produce only preflight evidence.

## 9. Downstream locks

DEC-279 does **not** authorize:

- historical-result dispatch;
- historical discovery execution;
- discovery-result production;
- proof retry/rerun/replacement;
- reserved 2023-2026 access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## 10. Next gate

After the proof run becomes terminal, DEC-277 must review the exact run/jobs/artifacts/preflight evidence.

A later DEC-280 may freeze that reviewed fail-closed proof. Only after that proof is accepted may any separate historical-result authorization be designed.
