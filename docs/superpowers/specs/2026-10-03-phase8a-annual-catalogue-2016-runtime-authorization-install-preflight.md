# Phase 8A — 2016 Runtime Authorization Install Preflight

**Date:** 2026-10-03  
**Status:** READ-ONLY INSTALL PREFLIGHT / LIVE RUNTIME UNCHANGED  
**Decision:** DEC-506  
**Predecessor:** DEC-505

DEC-506 defines the read-only preflight for the future two-file repository mutation that installs the 2016 runtime authorization after concrete DEC-503/504 evidence exists.

It pins:
- DEC-504 execution-authorization source blob `19d95a11e3ae1684d28ab17020f78bea39003bc8`;
- DEC-505 dormant-plan source blob `bc122efd630dc446621fefa53e37d8e100e025d2`;
- current runtime blob `ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b`;
- dormant 2016 gate template blob `87c00381c5c12a0593378f565e6be4bad003514f`;
- dormant 2016-wired runtime target blob `d7d3713cb3259e793c448153fd75ca043f511389`.

A valid preflight requires:
- a canonical valid DEC-504 authorization receipt;
- exact current `main`;
- segment `2016`;
- expected run #3 / attempt 1;
- a positive previous annual-freeze run id;
- DEC-504 runtime installation and gate state still false;
- DEC-505 target gate still absent and current runtime still on the pre-2016 blob.

The future activation is exactly two files:
1. create `src/fmp/discovery/annual_pattern_catalogue_2016_runtime_authorization.py` from the frozen gate template;
2. replace `src/fmp/discovery/annual_pattern_catalogue_runtime.py` with the frozen 2016-wired runtime target.

DEC-506 is plan-only/read-only. Repository mutation, runtime activation, dispatch, historical execution/results, 2017+, Strategy V1, promotion, Phase 8B, demo/live, broker mutation, real-money action, and trading remain false.

## Next gate

`EXACT_ANNUAL_PATTERN_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_MUTATION`
