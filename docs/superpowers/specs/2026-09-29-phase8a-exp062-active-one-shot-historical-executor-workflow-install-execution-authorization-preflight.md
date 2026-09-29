# Phase 8A — EXP-062 Workflow Install-Execution Authorization Preflight

**Date:** 2026-09-29  
**Status:** READ-ONLY CURRENT-MAIN PREFLIGHT / NO INSTALL OR DISPATCH  
**Decision:** DEC-385  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-384

## Purpose

DEC-385 checks that the source-authorized future workflow-install execution
authorization remains valid on the exact current `main` commit before any
repository-hosted proof can advance.

It pins the exact DEC-384 install-execution authorization contract and dormant
executor workflow template, requires the active executor workflow path to remain
absent, and verifies that the historical-result slot is still unused.

## Read-only boundary

The CLI exposes only `plan`. There is no install, execute, advance, or workflow
dispatch surface.

A valid preflight requires:

- exact current-main head identity;
- DEC-384 contract blob `40a3164fe713baf4289099e829527abc3da94c6e`;
- dormant executor template unchanged;
- active executor workflow path absent;
- zero historical-result attempts;
- target run #2 / attempt 1;
- install-authorization source authorized;
- install-decision source authorized;
- install-execution authorization source authorized;
- actual install authorization still false.

Reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain locked.

## Next gate

The next safe gate is a repository-hosted, read-only first-run/attempt-1 proof of
this install-execution authorization preflight.
