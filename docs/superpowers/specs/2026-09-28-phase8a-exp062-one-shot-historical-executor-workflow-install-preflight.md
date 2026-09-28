# Phase 8A — EXP-062 One-Shot Historical Executor Workflow-Install Preflight

**Date:** 2026-09-28  
**Status:** READ-ONLY CURRENT-MAIN INSTALL PREFLIGHT / NO INSTALL OR DISPATCH  
**Decision:** DEC-349  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-348

## Purpose

DEC-349 adds a read-only current-main preflight for the DEC-348 source-authorized
future one-shot historical executor workflow installation.

The preflight proves that the expected future workflow path is still absent, current
main matches the requested head, and the sole historical-result slot remains unused.

## Source binding

DEC-349 pins the DEC-348 install-contract blob:

`111a56fdbb8844c119307465e7b7cf6a4d43d95a`

The expected future workflow path remains:

`.github/workflows/phase8a-exp062-one-shot-historical-executor.yml`

## Read-only checks

A valid preflight requires:

- exact `main` metadata and head;
- the future executor workflow path does not exist;
- the frozen EXP-062 proof remains the only discovery run;
- zero historical-result attempts;
- target run #2 / attempt 1;
- install-source authorization true;
- install authorization false;
- workflow installed false;
- executor availability false;
- dispatch false;
- execute mode false.

The CLI exposes only `plan`; there is no install, execute, or advance surface.

## Safety boundary

Rerun/retry/replacement, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

## Next gate

The next safe gate is a repository-hosted read-only proof of this workflow-install
preflight.
