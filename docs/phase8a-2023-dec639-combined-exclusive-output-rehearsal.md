# DEC-639 — Combined offline exclusive-output rehearsal (NEVER MERGE)

**DRAFT / CI EXPERIMENT ONLY / DO NOT LAND.** This snapshot exists to test all 23 2023 legacy offline assessment CLI output fixes together. It is not an authorization for GitHub merges, workflow dispatch, protected historical-data access, run385, broker actions, or trading.

## Exact source inputs

- Existing five-PR combined rehearsal [#801](https://github.com/Dtwosam/FMP/pull/801): `783590c3d966587563fc702f5e2512e337ca65de`. It already combines DEC-627 through DEC-631, including the five focused workflow checks; unchanged original base main is `53e203133bbc141b2f48c7b8b8241d56b35166a3`.
- [#805](https://github.com/Dtwosam/FMP/pull/805) DEC-635: `f4043e2247f30cd168050c61a80ea79769bac0d5` (8 paths; 4 CLIs).
- [#806](https://github.com/Dtwosam/FMP/pull/806) DEC-636: `f0e31b692e85029fd94515515a32c2cf6fb23ec1` (12 paths; 7 CLIs).
- [#807](https://github.com/Dtwosam/FMP/pull/807) DEC-637: `95a87aa917a5f77c6f36c0df37906723e1c9fa4a` (7 paths; 2 CLIs).
- [#808](https://github.com/Dtwosam/FMP/pull/808) DEC-638: `6035378bd73daea5b88fb534bf9ba12f35eb1097` (14 paths; 10 CLIs).

Overlay exactly **35 unique paths** from the four draft branch trees onto the #801 rehearsal tree, preserving each original Git blob SHA. The sole duplicated paths across the four proposals are `src/fmp/discovery/annual_pattern_catalogue_2023_external_report_create.py` (identical Git blob `a9e7f02c8959cd0e8b9b31fb007ba34107165c80`) and `tests/test_phase8a_annual_pattern_catalogue_2023_exclusive_report_creation.py` (identical Git blob `895db79eb1537c96be174de85e6e009ebaa6a49b`). They are included **once**, not cloned as separate implementations. The resulting branch adds this provenance note and a 23-CLI static integration inventory regression; no original source branch is modified.

## Acceptance criteria and limits

The PR-triggered CI must pass all five existing DEC-627–631 checks, historical/general tests (including DEC-635–639 regressions), package compilation, and Phase 3 acceptance on the **new exact head**. A passing test run does not prove concurrent parent-directory path safety, atomic/durable publication, immutable GitHub refs, independent reviews, or permission to land anything. The exclusive-create helper guards leaf no-clobber semantics only; tests also check preexisting external hardlinks are not rewritten.

Do not merge this derived snapshot or any review-blocked source PR. After acceptable independent reviews, the real 796→797→798 dependency chain and independent 799/800 changes require controlled landing, conflict reconciliation of the common helper/test blobs, new exact-head CI, and a separate final permission decision. No installed annual workflow/runtime or live authorizations were changed by this rehearsal.
