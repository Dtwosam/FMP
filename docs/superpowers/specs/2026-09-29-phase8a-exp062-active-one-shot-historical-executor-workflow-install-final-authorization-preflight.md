# Phase 8A — EXP-062 Final Workflow-Install Authorization Preflight

**Date:** 2026-09-29  
**Status:** READ-ONLY CURRENT-MAIN PREFLIGHT / NO INSTALL OR DISPATCH  
**Decision:** DEC-412  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-411

DEC-412 verifies the final source-only workflow-install authorization contract on
the exact current `main` commit.

A valid preflight requires:

- DEC-411 contract blob
  `30493981eb2e5663e1fe620026c2c0af0cc03dd9`;
- exact current-main head identity;
- active executor workflow path absent;
- historical-result slot still unused;
- target historical run #2 / attempt 1;
- all seven source-only gates true;
- actual workflow-install authorization false.

The CLI exposes only `plan`. There is no install, execute, advance, or workflow
dispatch surface.

## Next gate

The next safe gate is a repository-hosted, read-only first-run/attempt-1 proof of
this final authorization preflight.
