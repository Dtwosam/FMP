# Phase 8A — EXP-062 Connector Proof Bootstrap Recovery

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY RECOVERY CONTRACT / NO DISPATCH  
**Decision:** DEC-306  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-301 through DEC-305

## Problem

The installed DEC-303 one-shot proof executor is intentionally triggered by a push to
`main`. Two connector-created merges that changed its workflow path produced no
GitHub Actions run on the resulting main commits. No EXP-062 proof run exists.

DEC-306 does not weaken or rewrite DEC-303. It adds a separately named recovery
contract for this integration-specific trigger gap.

## Recovery constraints

The recovery path may be activated only by a later, dedicated pull-request workflow
job and only after the normal repository unit suite succeeds. The contract requires:

- exact clean `main` checkout captured at runtime and revalidated by both fresh DEC-302 plans;
- GitHub Actions `pull_request` context;
- base ref `main`;
- activation head ref `phase8a-dec307-exp062-proof-bootstrap-activation`;
- workflow attempt 1 only;
- two identical fresh DEC-302 zero-run plans;
- the unchanged DEC-303 plan validator and proof evidence builder;
- the unchanged sole proof command:
  `gh workflow run phase8a-exp062-discovery.yml --ref main`.

Any existing EXP-062 manual-main proof/history run causes the DEC-303 zero-run guard to
fail closed.

## Authority boundary

DEC-306 is source-only. It does not alter `.github/workflows/tests.yml`, install an
activation job, or dispatch the proof. Historical-result dispatch/execution, reserved
2023-2026 access, candidate compilation/promotion, Phase 8B, demo, broker/live,
real-money, and trading remain false.

A later DEC-307 activation may wire the reviewed recovery CLI into the existing
pull-request CI workflow after the normal unit suite, with exact-main checkout and
`actions: write` limited to that one guarded job.
