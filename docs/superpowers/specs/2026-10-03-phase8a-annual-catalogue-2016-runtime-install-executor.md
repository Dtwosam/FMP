# Phase 8A — Exact 2016 Runtime Install Executor

**Date:** 2026-10-03  
**Status:** BOUNDED REPOSITORY MUTATION / NO WORKFLOW DISPATCH  
**Decision:** DEC-515  
**Predecessors:** DEC-507, DEC-508, DEC-514

DEC-515 is the exact repository-hosted executor for the frozen two-file 2016 runtime authorization install.

It runs only after a successful DEC-514 activation-plan workflow and requires:
- the exact DEC-514 workflow/source identity;
- a unique unexpired DEC-514 activation-plan artifact with a verified GitHub SHA-256 digest;
- a valid DEC-507 action for exactly two mutations;
- current `main` still equal to the reviewed DEC-514 head immediately before mutation and immediately before push;
- the 2016 runtime-authorization target still absent;
- the current runtime still equal to the exact pre-install blob.

The executor copies only the frozen dormant templates into:
- `src/fmp/discovery/annual_pattern_catalogue_2016_runtime_authorization.py`;
- `src/fmp/discovery/annual_pattern_catalogue_runtime.py`.

It verifies both resulting Git blob SHAs, creates one normal non-force commit, and pushes that exact commit to `main`. After the push it builds and validates the concrete DEC-508 install receipt.

DEC-515 has no Actions-write permission and contains no workflow dispatch, rerun, retry, broker, order, real-money, or trading command.

## Next gate

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_DISPATCH_PREFLIGHT_ON_INSTALLED_MAIN`
