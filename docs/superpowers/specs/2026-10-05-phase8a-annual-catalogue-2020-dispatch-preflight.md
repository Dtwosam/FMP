# Phase 8A — 2020 Annual Catalogue Dispatch Preflight

**Date:** 2026-10-05  
**Status:** READ-ONLY / RUN 382 UNCONSUMED  
**Decision:** DEC-573

## Concrete source evidence

DEC-572 installer workflow run `37361230835` / attempt 1 completed successfully on
`2d57ea571111845cd58a34a0c25a89eabe233bcb`.

Its immutable install artifact is `11367191085` with digest
`sha256:5f0f9862b411a9da4f0c383259ef78dc9df842be4a58ee06c43374a0b774d716`.

The embedded DEC-572 receipt binds:

- install commit `3ee648808bc2982c02dd1cb10fd45911f6379dcb`;
- installed 2020 gate blob `695a50b418da752e1bd37d6302f209033ab611f5`;
- installed annual runtime blob `4e124365430672fa63825b272001937c60151644`;
- receipt fingerprint `1f77559f7aadfb83e338e467148d86b2a99850d69909e689f04604fa19c3e7b4`;
- predecessor successful 2019 annual run `37310525635`;
- future target annual run 382 / attempt 1.

## DEC-573 contract

DEC-573 is read-only. It requires:

- current main to descend from exact DEC-572 install commit;
- exact installed 2020 gate/runtime blobs;
- exact annual workflow history
  `{1 failure, 376 failure, 377–381 success}`;
- no annual run 382 or later;
- exact predecessor run `37310525635`.

It produces only a deterministic preflight artifact for segment 2020 / run 382 /
attempt 1. It contains no workflow-dispatch command and grants no repository
mutation, later-year execution, strategy/promotion, broker mutation, order
placement, real-money action, or trading authority.

## Next gate

`ANNUAL_PATTERN_CATALOGUE_2020_DISPATCH_AUTHORIZATION_BEFORE_RUN`
