# Phase 8A — 2016 Runtime Authorization Install Action

**Date:** 2026-10-03  
**Status:** SOURCE-ONLY EXACT MUTATION ACTION / LIVE RUNTIME UNCHANGED  
**Decision:** DEC-507  
**Predecessor:** DEC-506

DEC-507 compiles the exact repository mutation action required to install the 2016 runtime authorization after a concrete valid DEC-506 preflight.

The action is current-main-sensitive. If main moves after the DEC-506 receipt was built, DEC-507 fails closed.

The compiled mutation contains exactly two ordered actions:

1. Create
   `src/fmp/discovery/annual_pattern_catalogue_2016_runtime_authorization.py`
   from dormant template blob
   `87c00381c5c12a0593378f565e6be4bad003514f`.
2. Update
   `src/fmp/discovery/annual_pattern_catalogue_runtime.py`
   from expected current blob
   `ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b`
   to target blob
   `d7d3713cb3259e793c448153fd75ca043f511389`.

The action records standing operator autonomous-build authorization for that exact two-file repository mutation only.

DEC-507 does not itself mutate the repository. Runtime authorization remains uninstalled, the runtime gate remains inactive, workflow dispatch and historical execution/results remain false, and 2017+, Strategy V1, promotion, Phase 8B, demo/live, broker mutation, real-money action, and trading remain false.

## Next gate

`APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_ACTION`
