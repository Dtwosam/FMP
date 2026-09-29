# Phase 8A — EXP-062 Active Executor Workflow Install-Execution Preflight

**Date:** 2026-09-29  
**Status:** READ-ONLY CURRENT-MAIN PREFLIGHT / NO INSTALL OR DISPATCH  
**Decision:** DEC-391  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-390

## Purpose

DEC-391 checks that the source-authorized workflow install-execution contract is
still valid on the exact current `main` commit before any repository-hosted proof
or actual installation can advance.

It pins the exact DEC-390 contract and dormant executor workflow template, requires
the active executor workflow path to remain absent, and verifies that the
historical-result slot is still unused.

## Read-only boundary

The CLI exposes only `plan`. There is no install, execute, advance, or workflow
dispatch surface.

A valid preflight requires:

- exact current-main head identity;
- DEC-390 contract blob
  `a3507bf9d44426b88f877e0dfa3ce77d299acb20`;
- dormant executor template unchanged;
- active executor workflow path absent;
- zero historical-result attempts;
- target run #2 / attempt 1;
- all four source-only gates true;
- actual workflow-install authorization still false.

Reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain locked.

## Next gate

The next safe gate is a repository-hosted, read-only first-run/attempt-1 proof of
this install-execution preflight.
