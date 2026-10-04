# Phase 8A — 2018 Annual Catalogue Execution Authorization

**Date:** 2026-10-04  
**Status:** SOURCE-ONLY AUTHORIZATION / RUNTIME NOT INSTALLED  
**Decision:** DEC-546

## Concrete source preflight

DEC-546 consumes only the concrete DEC-545 artifact produced by workflow run
`37229319220` on head
`24fa329cbcf88192cdc19e63173edd55b3aa7eb5`:

- artifact ID: `11313083318`;
- artifact digest:
  `sha256:36f76bba9cd3cef5fd1b3236f3bc80ad62029edf9c493ce10d946b7bcadf18a4`;
- preflight fingerprint:
  `55b9378a78f54a99a9055da1ac0294e73c5e02434fc4ad17d38acea7ac5c6315`.

The preflight binds segment `2018` to predecessor segment `2017`, predecessor
run `37227536041`, and expected annual identity run `380` / attempt `1`.

## Authorization contract

DEC-546 authorizes the exact research contract for 2018 run 380 / attempt 1:

- annual workflow dispatch authority: yes, at contract level;
- historical artifact reads: yes;
- historical catalogue execution: yes;
- historical result production: yes.

This is source-only authorization. The current annual runtime is pinned at
`e9cbc76dc9e6866e80088d223498fbcc3b870fd1` and must not yet contain a
`2018` route or `require_2018_execution_authorized` gate.

Therefore:

- runtime authorization installed: no;
- runtime gate active: no;
- dispatch command present: no;
- dispatch action executed: no;
- rerun/retry/replacement authority: no;
- run 381+ authority: no;
- next-segment/cross-year/strategy/promotion/Phase 8B authority: no;
- broker mutation, demo/live order, real-money, and trading authority: no.

## Next gate

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2018_RUNTIME_AUTHORIZATION_PLAN`
