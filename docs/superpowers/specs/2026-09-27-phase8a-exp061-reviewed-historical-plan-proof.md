# Phase 8A — EXP-061 Reviewed Historical Plan Proof

**Date:** 2026-09-27  
**Status:** REVIEWED / SLOT VERIFIED AVAILABLE / EXECUTION STILL LOCKED  
**Decision:** DEC-284  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-283

## Purpose

DEC-284 freezes the exact successful merged-main read-only historical-slot proof produced by DEC-283.

It introduces no dispatch, execution, result-production, retry, replacement, or trading authority.

## Exact proof run

DEC-283 merged to main at:

`7fd3a9e878bf2760850037548e93dc1e8173c0c1`

The repository-hosted proof run is:

- run id: `36323674455`;
- workflow: `phase8a-exp061-historical-plan`;
- path: `.github/workflows/phase8a-exp061-historical-plan.yml`;
- event: `push`;
- branch: `main`;
- head: `7fd3a9e878bf2760850037548e93dc1e8173c0c1`;
- attempt: `1`;
- terminal status: `completed`;
- conclusion: `success`.

Every proof step completed successfully, including:

- exact merged-main checkout;
- frozen DEC-280/281/282 source identity checks;
- pinned runtime installation;
- clean-worktree proof;
- live main/run-inventory reads;
- exact DEC-282 plan execution;
- slot-available validation;
- immutable artifact upload.

## Exact proof artifact

Exactly one historical-plan proof artifact exists:

- artifact id: `10932743232`;
- name: `exp061-dec283-historical-plan-7fd3a9e878bf2760850037548e93dc1e8173c0c1`;
- digest: `sha256:a71585da8c7e858d7ed309cf52965c5a0fbb7ef42b65e28a18933792eeb9460a`;
- expired: `false`.

The downloaded artifact ZIP independently hashes to the same SHA-256 digest.

It contains exactly one file:

`historical-plan.json`

Plan raw SHA-256:

`7cbe58c3ec256ff0973c9baa86e109486f0c2e37eaa973bf053fa1337cc1849e`

Plan canonical SHA-256:

`605af14b35bdf132217340e7701263bfaf24d6280d6e45edbb43d2d1debc35de`

## Frozen plan meaning

The exact plan proves:

- operator decision: `DEC-282`;
- authorization decision: `DEC-281`;
- expected head equals DEC-283 merged main;
- frozen proof run id: `36319888985`;
- frozen proof run count: `1`;
- historical-result attempt count: `0`;
- historical-result run id: null;
- historical-result slot consumed: `false`;
- stage: `EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE`;
- source-governance slot authorization: `true`;
- planned future command: `gh workflow run phase8a-exp061-discovery.yml --ref main`.

The command remains evidence only. DEC-284 does not execute it.

## Frozen source bindings

DEC-284 binds:

- DEC-283 proof workflow blob: `7c2d7409d1a05ce287cc36f5371a85273a6a027b`;
- DEC-282 historical operator blob: `1ffef37d94b04a8206f665c375dc0b2642c4caa9`;
- DEC-282 historical operator CLI blob: `4d667d05ef2a5bd672cb9d98a81f13dd2ba9370c`;
- DEC-281 historical authorization blob: `1eab1cee2fc81441cf1c3168cc73275cd29addf5`.

Reviewed-proof implementation:

`src/fmp/discovery/historical_plan_result_decision.py`

Git blob:

`14d9c559eaa33e5cb217baaf3ed2597091735b18`

Focused tests:

`tests/test_phase8a_exp061_reviewed_historical_plan_proof.py`

Git blob:

`7cf308e67232b441530230555fe19230d89b0304`

## Locks preserved

DEC-284 keeps false:

- historical-result dispatch;
- historical discovery execution;
- discovery-result production;
- rerun;
- retry;
- replacement;
- reserved 2023-2026 robustness access;
- candidate compilation;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

No historical-result slot is consumed.

## Next gate

After DEC-284 merges green, the next safe step is a separate source-only historical execution-authorization transition.

That transition may supersede the current runtime gate only after binding this reviewed DEC-284 proof. It must preserve:

- exactly one future historical attempt;
- attempt 1 only;
- no retry/rerun/replacement;
- 2015-2022 historical range only;
- 2023-2026 reserved robustness still closed;
- no candidate compilation or promotion;
- no Phase 8B/demo/live/real-money/trading authority.

A later one-shot executor may be considered only after that execution-authorization source is itself reviewed and merged.
