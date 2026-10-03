# Phase 8A — 2016 Annual Catalogue Execution Preflight

**Date:** 2026-10-03  
**Status:** SOURCE-READY READ-ONLY 2016 PREFLIGHT  
**Decision:** DEC-503  
**Predecessor:** DEC-502

DEC-503 defines the read-only preflight for the first 2016 annual-pattern-catalogue run.

It pins:
- DEC-502 runtime-binding source blob `505e9dcbfc518e7fc00b603cafef44077d105cfa`;
- live runtime source blob `ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b`;
- repaired annual workflow blob `f7e65ee95f472918e390bceedd7cf2f38bbf7e92`.

The preflight requires:
- a semantically valid concrete DEC-502 binding for the successful 2015 replacement run;
- exact current `main`;
- exactly two prior annual workflow runs:
  - run #1 / attempt 1: the frozen failed 2015 first run;
  - run #2 / attempt 1: the successful 2015 replacement run bound by DEC-502;
- target annual segment `2016`;
- predecessor segment exactly `2015`;
- `previous_annual_freeze_run_id` equal to the successful 2015 run id;
- expected next workflow identity #3 / attempt 1.

DEC-503 exposes only a `plan` CLI.

Annual workflow dispatch, historical reads, catalogue execution/results, cross-year
result production, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker
mutation, real-money action, and trading remain false.

## Next gate

`ANNUAL_PATTERN_CATALOGUE_2016_EXECUTION_AUTHORIZATION_BEFORE_RUN`
