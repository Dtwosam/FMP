# Phase 8A — EXP-062 One-Shot Historical Executor Source Proof

**Date:** 2026-09-28  
**Status:** REPOSITORY-HOSTED READ-ONLY SOURCE PROOF / NO DISPATCH  
**Decision:** DEC-338  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-334, DEC-336, DEC-337

## Purpose

DEC-338 adds a repository-hosted proof of the DEC-337 one-shot historical executor
source contract.

The proof rebuilds the concrete DEC-336 activation-preflight runtime evidence from the
real DEC-332 proof artifact, builds a fresh DEC-331 activation preflight against current
main, and then evaluates the DEC-337 source contract.

It never dispatches the historical workflow.

## Trigger and permissions

The workflow:

- runs only on pushes to `main` touching the frozen executor-source chain;
- requires workflow run #1 / attempt 1;
- checks out exact merged main;
- uses only `contents: read` and `actions: read`;
- has no `actions: write` permission;
- has no `workflow_dispatch`, pull-request, or scheduled trigger.

## Frozen evidence replay

DEC-338 downloads the immutable DEC-332 artifact `10973597441` and requires ZIP
SHA-256:

`ee6e7ac2e8c18e1f8d276bba14ca942e20615143316ac185f4b814333804c2d5`

It then replays DEC-333 / DEC-335 / DEC-336 before evaluating DEC-337.

## Fresh slot proof

The workflow also fetches current main and the exact EXP-062 manual-main run inventory
and rebuilds DEC-331. A valid proof requires:

- historical-result attempts remain zero;
- the slot remains unconsumed;
- target remains run #2 / attempt 1;
- the historical command remains frozen as evidence only;
- DEC-337 source authorization is true;
- historical executor availability, actual dispatch, execute mode, rerun/retry/
  replacement, reserved data, candidate/promotion, Phase 8B, demo/live, real-money,
  and trading remain false.

## Artifact

A successful proof uploads only:

`one-shot-historical-executor-source-contract.json`

under:

`exp062-dec338-one-shot-historical-executor-source-<merged-main-sha>`

No historical discovery result is produced.

## Next gate

After real successful DEC-338 runtime evidence exists, it must be reviewed and frozen
before any dispatch-capable one-shot executor workflow is considered.
