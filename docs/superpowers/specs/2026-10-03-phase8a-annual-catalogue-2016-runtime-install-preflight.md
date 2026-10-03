# Phase 8A — 2016 Runtime Authorization Install Preflight

**Date:** 2026-10-03  
**Status:** READ-ONLY INSTALL PREFLIGHT / MUTATION LOCKED  
**Decision:** DEC-505  
**Predecessor:** DEC-504

DEC-505 defines the read-only preflight for installing the scoped 2016 execution gate into the live annual-catalogue runtime.

It pins:
- DEC-504 authorization source blob `19d95a11e3ae1684d28ab17020f78bea39003bc8`;
- current live runtime blob `ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b`;
- repaired annual workflow blob `f7e65ee95f472918e390bceedd7cf2f38bbf7e92`.

The preflight requires:
- a valid DEC-504 authorization receipt;
- exact current `main`;
- the current runtime to contain no existing 2016 authorization import or gate.

It emits exactly one planned mutation:
- target: `src/fmp/discovery/annual_pattern_catalogue_runtime.py`;
- operation: update;
- expected current blob: `ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b`;
- required authorization module: `annual_pattern_catalogue_2016_execution_authorization`;
- required gate: `require_2016_execution_authorized`;
- scope: 2016, run #3 / attempt 1.

DEC-505 is plan-only. Repository mutation, runtime installation, live dispatch,
historical execution/results, 2017+, Strategy V1 synthesis, promotion, Phase 8B,
demo/live, broker mutation, real-money action, and trading remain false.

## Next gate

`CONCRETE_2016_RUNTIME_AUTHORIZATION_INSTALL_MUTATION_AFTER_PREFLIGHT`
