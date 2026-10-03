# Phase 8A — Recovered Exact 2016 Runtime Install Executor

**Date:** 2026-10-03  
**Status:** BOUNDED REPOSITORY MUTATION / NO WORKFLOW DISPATCH  
**Decision:** DEC-518  
**Predecessors:** DEC-507, DEC-508, DEC-514, DEC-517

DEC-518 is installed on the same recovery merge as DEC-517 so it is already present before the successful DEC-513 → DEC-514 workflow-run chain can complete.

It runs only after a successful DEC-514 activation-plan workflow and requires:
- the recovered DEC-514 workflow blob `3d18bd39390b3dd2ec31860c30b8c4326ba23005`;
- one unique unexpired DEC-514 activation-plan artifact with a verified GitHub SHA-256 digest;
- the exact DEC-507 two-file action plus the concrete DEC-502 runtime binding carried by that artifact;
- current `main` still equal to the reviewed DEC-514 head immediately before mutation and immediately before push;
- the 2016 runtime-authorization target still absent;
- the current annual runtime still equal to its exact pre-install blob.

DEC-518 copies only the two frozen templates into the 2016 gate and annual-runtime target paths, verifies the resulting Git blob SHAs, creates one normal non-force commit, pushes that exact commit to `main`, and then builds the concrete DEC-508 install receipt.

DEC-518 has no Actions-write permission and contains no workflow dispatch, rerun, retry, broker, order, real-money, or trading command.

## Next gate

`READ_ONLY_POST_INSTALL_2016_DISPATCH_PLAN_ON_DEC_518_RECEIPT`
