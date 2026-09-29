# Phase 8A — EXP-062 Active Executor Workflow Install-Decision Preflight

**Date:** 2026-09-29  
**Status:** READ-ONLY CURRENT-MAIN PREFLIGHT / NO INSTALL OR DISPATCH  
**Decision:** DEC-379  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-378

## Purpose

DEC-379 checks that the source-authorized future install decision is still valid on
the exact current `main` commit before any repository-hosted proof is allowed.

It pins the exact DEC-378 install-decision contract and dormant executor workflow
template, requires the active executor workflow path to remain absent, and verifies
that the historical-result slot is still unused.

## Read-only boundary

The CLI exposes only `plan`. There is no install, execute, advance, or workflow
dispatch surface.

A valid preflight requires:

- exact current-main head identity;
- DEC-378 contract blob
  `4bdaa6f48b2a0d8ea467c7cbd1869358749660e5`;
- dormant executor template unchanged;
- active executor workflow path absent;
- zero historical-result attempts;
- target run #2 / attempt 1;
- install-decision source authorized;
- actual install authorization still false.

Reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain locked.

## Next gate

The next safe gate is a repository-hosted, read-only first-run/attempt-1 proof of
this install-decision preflight.
