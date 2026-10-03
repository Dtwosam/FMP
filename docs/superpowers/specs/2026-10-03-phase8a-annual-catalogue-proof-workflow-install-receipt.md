# Phase 8A — Annual Catalogue Preflight Proof Workflow Installation Receipt

**Date:** 2026-10-03  
**Status:** PROOF WORKFLOW INSTALLED / DISPATCH LOCKED  
**Decision:** DEC-485  
**Predecessor:** DEC-484

DEC-485 records completion of the single repository mutation explicitly authorized
after DEC-484: install the annual-catalogue install-preflight proof workflow at:

`.github/workflows/phase8a-annual-catalogue-workflow-install-preflight-proof.yml`

The installed file is byte-for-byte identical to the frozen dormant template and
therefore has Git blob SHA:

`0d6c93e2af04501f9ac2589fd24d6672b2b41910`

DEC-485 also pins the DEC-484 authorization-preflight source blob:

`ab434212007f3777fa4436a51268438ea44be6dd`

The single-file installation authorization is consumed by this transition. Future
repository mutation is not authorized by DEC-485.

The installed proof workflow remains manual-only via `workflow_dispatch` and has
only `contents: read` and `actions: read` permissions. It can build and upload
the exact DEC-480 read-only annual-workflow install preflight evidence. It cannot
install or dispatch another workflow and contains no historical catalogue execution
surface.

Current authority:
- proof-workflow installation: completed;
- proof-workflow availability: true;
- future repository mutation: false;
- proof-workflow dispatch: false;
- annual-workflow installation/dispatch: false;
- historical artifact reads/execution/result production: false;
- cross-year result production and Strategy V1 synthesis: false;
- Phase 8B, demo/live, broker mutation, real-money action, and trading: false.

## Next gate

`EXPLICIT_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_BEFORE_RUN`

A separate operator authorization is required before the installed proof workflow
may be dispatched.
