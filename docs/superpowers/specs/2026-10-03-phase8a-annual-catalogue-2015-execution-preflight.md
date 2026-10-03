# Phase 8A — 2015 Annual Catalogue Execution Preflight

**Date:** 2026-10-03  
**Status:** READ-ONLY FIRST-RUN PREFLIGHT / EXECUTION LOCKED  
**Decision:** DEC-492  
**Predecessor:** DEC-491

DEC-492 defines the read-only preflight for the first 2015 annual-pattern-catalogue
run after the exact workflow installation.

It pins:
- DEC-491 install-receipt source blob
  `970ab466dfa5f87c6955ad65da4653a993e9d6fd`;
- DEC-475 runtime source blob
  `0044c19575ec005a31ab98beefccfc57fe9e72da`;
- active annual-workflow blob
  `31633e87b79551f5b7dfa6b0deb76a82eb070129`.

The preflight requires:
- exact current `main` identity;
- installed and available annual workflow;
- annual-workflow run inventory exactly empty;
- first expected annual run #1 / attempt 1;
- exact annual segment `2015`;
- no predecessor segment and no previous freeze run;
- DEC-475 historical artifact reads, catalogue execution, and result production
  all still false.

DEC-492 exposes only a `plan` CLI. It has no run, dispatch, or execute command and
contains no `gh workflow run` action.

Annual workflow dispatch, historical artifact reads, annual catalogue execution,
result production, next-segment execution, cross-year results, Strategy V1
synthesis, promotion, Phase 8B, demo/live, broker mutation, real-money action, and
trading remain false.

## Next gate

`EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_EXECUTION_AUTHORIZATION_BEFORE_RUN`
