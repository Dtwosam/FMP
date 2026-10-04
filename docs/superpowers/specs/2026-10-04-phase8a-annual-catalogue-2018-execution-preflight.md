# Phase 8A — 2018 Annual Catalogue Execution Preflight

**Date:** 2026-10-04  
**Status:** CONCRETE READ-ONLY PREFLIGHT / RUN 380 LOCKED  
**Decision:** DEC-545

## Concrete predecessor

DEC-544 concrete 2017 runtime evidence was recovered without rerunning annual
research:

- recovery workflow run: `37228767187`;
- recovery head: `8169c07142fee231cf0fbe539954b876e2f0e240`;
- artifact: `11313481023`;
- artifact digest:
  `sha256:f48dd73bbae1587bf8c6e97408295ab94761ab4536c7124532ef5b6f55c2d1d1`;
- binding fingerprint:
  `a454e3eef8a51260cc07f9103a7de0208f5408a18686bb1249ad05e349edd9ae`;
- 2017 freeze fingerprint:
  `ed579f80f947f9a04731b4a20e675c98e2101884c874fa385df5999ef419ff8b`.

The bound predecessor is annual run `37227536041`, global run `379`,
attempt `1`, segment `2017`.

## DEC-545

DEC-545 is a read-only preflight for annual segment `2018`. It requires:

- exact annual history:
  - run 1 failure;
  - run 376 failure;
  - run 377 success for 2015;
  - run 378 success for 2016;
  - run 379 success for 2017;
- the exact recovered DEC-544 binding and fingerprints;
- current `main` to equal the preflight landing head;
- the corrected annual workflow blob
  `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`;
- no annual run 380 or later.

The resulting preflight freezes only:

- annual segment: `2018`;
- predecessor segment: `2017`;
- predecessor run ID: `37227536041`;
- expected next annual identity: run `380` / attempt `1`.

## Authority boundary

DEC-545 grants no workflow dispatch, historical artifact read, historical
execution, historical result production, next-segment execution, cross-year
synthesis, Strategy V1 synthesis, promotion, Phase 8B, broker mutation,
demo/live order, real-money action, or trading authority.

The next gate is
`ANNUAL_PATTERN_CATALOGUE_2018_EXECUTION_AUTHORIZATION_BEFORE_RUN`.
