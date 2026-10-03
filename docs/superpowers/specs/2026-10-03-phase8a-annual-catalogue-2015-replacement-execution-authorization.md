# Phase 8A — 2015 Replacement Execution Authorization

**Date:** 2026-10-03  
**Status:** REPLACEMENT RUN #2 / ATTEMPT 1 AUTHORIZED / NOT STARTED  
**Decision:** DEC-498  
**Predecessor:** DEC-497

DEC-498 records standing operator authorization to continue the annual-catalogue
build chain autonomously through exactly one repaired 2015 replacement run.

It pins:
- DEC-497 replacement-preflight source blob
  `c69f8a9bf1130ae776b06670fba0c63c935afdc1`;
- DEC-495 failure-receipt source blob
  `1ae96e83dc5d895dce1c5f981f1c785401de22f5`;
- DEC-496 upload-repair source blob
  `adfa75b352a561667b8c23efbcfb07af804d1131`;
- repaired workflow blob
  `f7e65ee95f472918e390bceedd7cf2f38bbf7e92`.

Authorized scope:
- annual segment `2015` only;
- replacement workflow run #2 only;
- attempt 1 only;
- historical artifact reads, catalogue execution, and result production only for
  that exact replacement identity.

The live runtime now recognizes run #2 / attempt 1 separately from the consumed
first-run authorization. The original DEC-493 runtime is preserved as an exact
snapshot at blob `4f23996b90b4253af06774d0330003179264c8ee`.

Rerunning failed run #1, retrying it as attempt 2, run #3+, 2016+, Strategy V1,
promotion, Phase 8B, demo/live, broker mutation, real-money action, and trading
remain false.

## Next gate

`EXACT_2015_REPLACEMENT_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`
