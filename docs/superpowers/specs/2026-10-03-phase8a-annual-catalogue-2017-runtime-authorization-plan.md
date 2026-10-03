# Phase 8A — Dormant 2017 Runtime Authorization Plan

**Date:** 2026-10-03  
**Status:** SOURCE-ONLY DORMANT PLAN / NO REPOSITORY MUTATION  
**Decision:** DEC-525  
**Predecessors:** DEC-523, DEC-524

DEC-525 defines the dormant 2017 runtime authorization gate and runtime target for exact annual workflow run 378 / attempt 1.

The plan pins:
- exact DEC-523 and DEC-524 source blobs;
- corrected annual workflow blob;
- expected post-2016 runtime base blob `995bb46ddd95563f904243c78ae4fc3cf3308968`;
- exact dormant 2017 gate template;
- exact runtime target template that preserves the 2015 replacement route (376), 2016 route (377), and adds only the 2017 route (378).

The current branch does not claim that the post-2016 runtime base is installed. Repository mutation, runtime activation, workflow dispatch, later-year execution, promotion, broker mutation, orders, real-money action, and trading remain false.

## Next gate

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC524`
