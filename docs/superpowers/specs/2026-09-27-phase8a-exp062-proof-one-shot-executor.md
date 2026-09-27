# Phase 8A — EXP-062 One-Shot Gate-Proof Executor

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY PROOF EXECUTOR / HISTORICAL RESULT STILL LOCKED  
**Decision:** DEC-303  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-302

## Purpose

DEC-303 adds the only repository-hosted executor allowed to submit the first EXP-062 **proof-only** manual-main run.

This proof run exists solely to demonstrate that the installed DEC-300 workflow fails closed at the DEC-299 execution gate. It is not a historical discovery result and does not consume a historical-result slot.

## One-shot prerequisites

The executor requires:

- exact merged `main`;
- executor workflow run number `1`;
- executor run attempt `1`;
- zero existing EXP-062 manual-main discovery-workflow runs;
- two identical fresh DEC-302 plans;
- both plans at the executor merged-main head;
- the exact planned command:

`gh workflow run phase8a-exp062-discovery.yml --ref main`

Any drift fails closed.

## Exact source pins

The executor workflow pins:

- active EXP-062 discovery workflow: `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`;
- DEC-299 workflow source: `e20ded13de24f99e8ea6cfdc6cb0d1309d984f24`;
- DEC-300 workflow install: `febb2bc00342364c67a75c69439136079eba0a2c`;
- DEC-301 proof contract: `dcc513d1918e95e2bc0bc02a04774291c6b340c0`;
- DEC-302 proof operator: `bc33c377ee9865766613a3ad64ddd9fd751d88fa`;
- DEC-302 operator CLI: `1b3525d8424a83bd02f46439eeab19956686b1c9`;
- DEC-303 executor core: `b5963636901b5caba1730f8a969dd3f9a1bf1979`;
- DEC-303 executor CLI: `1ff34425b4240312324ae2513fa6d747c0579982`;
- pinned runtime: `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

## Dispatch and post-check

Only DEC-303 sets **proof dispatch authorization** true.

After submitting the command, the executor requires exactly one EXP-062 manual-main run and verifies:

- workflow run number `1`;
- attempt `1`;
- head equals the DEC-303 merged-main head;
- positive run id.

Executor evidence records:

- proof dispatch submitted: true;
- historical-result slot consumed: false;
- historical result claimed: false.

## Frozen implementation

Executor source:

`src/fmp/discovery/exp062_proof_executor.py`

Git blob:

`b5963636901b5caba1730f8a969dd3f9a1bf1979`

Executor CLI:

`scripts/phase8a_exp062_proof_executor.py`

Git blob:

`1ff34425b4240312324ae2513fa6d747c0579982`

Executor workflow:

`.github/workflows/phase8a-exp062-proof-one-shot-execute.yml`

Git blob:

`45cfc626f82b4a05ed619d9eeffdb6bd2fa0e04a`

Focused tests:

`tests/test_phase8a_exp062_proof_executor.py`

Git blob:

`68b05897c9d7f9785bbd287057eded5f23a9d12e`

## Downstream locks

DEC-303 keeps false:

- historical-result dispatch;
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

## Next gate

DEC-303 may merge only after DEC-299/300/301/302 are green and merged.

Its merged-main executor may submit exactly one proof run. That run must then be terminally reviewed under DEC-301 and frozen as immutable evidence before any historical-result slot is considered.
