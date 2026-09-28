# Phase 8A — EXP-062 Connector Proof Bootstrap Activation

**Date:** 2026-09-28  
**Status:** STACKED ACTIVATION / DISABLED UNTIL BASE IS MAIN  
**Decision:** DEC-307  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-306

## Purpose

DEC-307 wires the reviewed DEC-306 recovery CLI into the existing repository test
workflow because connector-created merges did not materialize the original DEC-303
push-only executor.

The activation job is intentionally stacked on the DEC-306 branch first. While its PR
base is not `main`, the job-level guard is false and no proof can be dispatched.

## Activation guard

The job may run only when all of the following are true:

- event is `pull_request`;
- base ref is `main`;
- head ref is exactly
  `phase8a-dec307-exp062-proof-bootstrap-activation`;
- head repository is exactly the current repository;
- pull request number is exactly `451`;
- the normal `unit-tests` job completed successfully first;
- workflow attempt is 1.

The activation job checks out live `main`, requires a clean checkout equal to
`origin/main`, pins the frozen EXP-062 workflow/proof/DEC-306 source blobs, installs
only the pinned proof runtime, then invokes the DEC-306 CLI.

DEC-306 in turn requires two identical fresh zero-run DEC-302 plans for that exact
checkout head and delegates validation/evidence construction to unchanged DEC-303
code. The only dispatch command is:

`gh workflow run phase8a-exp062-discovery.yml --ref main`

After submission the job requires exactly one matching manual-main EXP-062 run,
workflow run #1 / attempt 1, at the same checked-out main head, and uploads immutable
bootstrap evidence.

## Authority boundary

DEC-307 may create only the fail-closed proof run. It does not authorize a historical
result run, historical discovery execution, reserved 2023-2026 access, candidate
compilation/promotion, Phase 8B, demo, broker/live, real-money, or trading.
