# DEC-1547 — Isolate aggregate JSON object and array budget boundaries

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1793 at `91493b64e84efcafcafdb25347968473eda9782d`. Correct three inherited tests that previously exercised multiple resource ceilings at once and add **8 synthetic regression tests** (**2,690 proposed source-defined methods**).

The #1792 historical/general CI job failed `test_json_exact_aggregate_object_members_reaches_shape`: 32,768 one-member objects were put in a single top-level array, violating the independent 16,384-item per-array ceiling before the intended 32,768-object-member exact-boundary check. The test expected `BUNDLE_SHAPE_UNREVIEWED` even though `BUNDLE_JSON_GRAMMAR_UNREVIEWED` is required by the earlier array budget. Rearrange fixture objects into 16,384 pairs to isolate the total object-member exact boundary; add the extra member to the first pair for the one-over case. Similarly disambiguate the stdin no-echo aggregate limit test.

Additional synthetic tests independently lock in array and object member exact/over boundaries, no counting of empty object members, document-level state reset, mixed small positive controls and never-authorizing verdict flags. Neither JSON limits nor scanner implementation are relaxed or modified. These tests authenticate no provider evidence and grant no protected original or annual-run authority.

Own exact-head Phase 3 and historical/general CI plus independent qualified review required. DEC-650/#820 independent protected-original OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 admission remain **BLOCKED**. No protected execution/retry, originals/archive/artifact access, workflow/security-control change, merge, deployment or trading.
