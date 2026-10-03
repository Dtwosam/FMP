# Phase 8A — 2015 Run #1 Failure Receipt

**Date:** 2026-10-03  
**Status:** FIRST RUN CONSUMED / FAILED BEFORE CELL EXECUTION  
**Decision:** DEC-495  
**Predecessor:** DEC-494

DEC-495 binds the first authorized 2015 annual-pattern-catalogue invocation.

- run id: `37126711695`;
- run number / attempt: `1 / 1`;
- head: `fd85a886d07234ad584dcca08692b37e6af54b2e`;
- preflight job: `111213380390`;
- run conclusion: `failure`;
- failing step: `Upload annual catalogue preflight evidence`.

All preflight validation steps before upload succeeded, including the exact EXP-044
source validation, the scoped 2015 execution gate, and the no-predecessor check.

The upload failed because `actions/upload-artifact@v6` used its default
`include-hidden-files: false` while the workflow stored evidence under the hidden
directory `.preflight`.

No annual cell executed. No catalogue result or annual freeze was produced.

The first-run authorization is consumed. Rerun, retry, and replacement-run
authorization remain false.

## Next gate

Repair hidden artifact uploads, then require a separate explicit 2015 replacement
run authorization.
