# Phase 8A — EXP-062 Dormant One-Shot Historical Executor Source Proof

**Date:** 2026-09-28  
**Status:** REPOSITORY-HOSTED READ-ONLY DORMANT SOURCE PROOF / ACTIVE EXECUTOR ABSENT  
**Decision:** DEC-356  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-354, DEC-355

## Purpose

DEC-356 adds a push-to-main, first-run/attempt-1 read-only proof of the DEC-355
dormant one-shot historical executor workflow source.

The proof validates the exact DEC-354/355 source chain, the disabled executor
template blob, and the active discovery workflow source while explicitly requiring
that the active executor workflow path does not exist.

## Trigger and permissions

The workflow:

- runs only on pushes to `main` touching the frozen dormant-source chain;
- requires workflow run #1 / attempt 1;
- checks out exact merged main;
- uses only `contents: read` and `actions: read`;
- has no `actions: write` permission;
- has no `workflow_dispatch`, pull-request, or scheduled trigger.

## Frozen identities

DEC-356 pins:

- DEC-354 installation-source contract:
  `e4fc6a7d1faaca50bc6936597f0e8b66fe096985`;
- DEC-355 dormant source validator:
  `003e44126d9d6a807efd51b5a589128f6d4b5aac`;
- dormant executor template:
  `51ce87584369be957482460d81649adb1cb9f05d`;
- active discovery workflow:
  `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`.

## Proof behavior

A valid proof requires:

- active executor workflow path absent;
- DEC-355 stage frozen and active workflow uninstalled;
- dormant template present and dispatch-capable only if later installed;
- zero historical-result attempts;
- target run #2 / attempt 1;
- workflow install authorization false;
- workflow installed false;
- executor availability false;
- historical dispatch false;
- execute mode false;
- rerun/retry/replacement and all downstream trading authority false.

The proof never installs or dispatches anything.

## Artifact

A successful run uploads only:

`dormant-one-shot-historical-executor-workflow-source.json`

under:

`exp062-dec356-dormant-one-shot-historical-executor-source-<merged-main-sha>`

## Next gate

After real successful DEC-356 runtime evidence exists, it must be reviewed and frozen
before any active executor workflow installation is considered.
