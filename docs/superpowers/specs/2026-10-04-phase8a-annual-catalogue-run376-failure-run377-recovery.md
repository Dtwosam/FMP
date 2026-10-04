# Phase 8A — Run-376 Failure and Fresh Run-377 Recovery

**Date:** 2026-10-04  
**Status:** SOURCE-READY RECOVERY / RUN 376 IMMUTABLE FAILURE  
**Decisions:** DEC-526, DEC-527, DEC-528

## Live evidence

Annual workflow run `37191637168` executed as global run 376 / attempt 1 on
main commit `4c14fa7db6eb812b89ecb79201f7e298fa9c04f3` and failed in the
2015 preflight before any annual cell ran.

The failure was caused by the historical DEC-491 installed-workflow validator
still requiring the pre-DEC-520 annual workflow blob. The corrected active
workflow remains exact blob
`09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`.

Run 376 is not retried or rerun.

## DEC-526 — immutable run-376 failure receipt

DEC-526 binds the exact failed run, failed preflight job, and skipped downstream
annual jobs. It records that no annual result was produced and grants no retry,
rerun, replacement, later-year, broker, order, real-money, or trading authority.

## Corrected installed-workflow state

A new corrected installed-state validator preserves the historical DEC-491
source and dormant template while validating the distinct DEC-520 corrected
active workflow. Historical evidence is not rewritten.

## DEC-527 — fresh 2015 run-377 authorization

DEC-527 authorizes only:

- annual segment `2015`;
- global annual workflow run 377;
- attempt 1;
- the corrected active annual workflow;
- historical artifact reads, annual catalogue execution, and result production
  required for that single fresh run.

It explicitly denies a rerun or retry of run 376 and denies run 378 or later.

## DEC-528 — exact dispatch receipt

The repository-hosted recovery workflow is advanced to its exact third push run.
It requires the annual inventory to be exactly failed run 1 and failed run 376,
builds DEC-526 and DEC-527, and may dispatch exactly one fresh 2015 run 377 /
attempt 1. It rejects any annual run 378 or later before recording DEC-528.

## 2016 run-number rebind

Because run 377 is now reserved for the fresh 2015 execution, the existing
DEC-503 through DEC-522 2016 chain is rebound to exact global run 378 /
attempt 1. Its predecessor inventory is exactly:

1. failed run 1;
2. failed run 376;
3. successful 2015 run 377.

DEC-521 may dispatch only 2016 run 378. DEC-522 reviews only successful 2016
run 378. Run 379+, 2017 execution, Strategy V1 synthesis, promotion, Phase 8B,
broker mutation, demo/live orders, real-money action, and trading remain locked.
