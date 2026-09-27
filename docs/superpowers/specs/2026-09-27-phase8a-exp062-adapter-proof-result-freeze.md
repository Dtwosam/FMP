# Phase 8A — EXP-062 Adapter Proof Result Freeze

**Date:** 2026-09-27  
**Status:** VERIFIED REAL-DATA REPAIR PROOF / HISTORICAL DISCOVERY STILL LOCKED  
**Decision:** DEC-297  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-294, DEC-295, DEC-296

## Exact proof run

The clean DEC-294 proof merged at:

`5e235938dc7e8eb467f59ca85ae4b6e1d5179475`

Merged-main proof run:

- run id: `36348366166`;
- workflow: `phase8a-exp062-adapter-proof`;
- event: `push`;
- branch: `main`;
- workflow run number: `1`;
- attempt: `1`;
- conclusion: `success`.

Exactly ten jobs completed successfully:

- nine pair/timeframe adapter probes;
- one aggregate proof job.

Exactly ten non-expired artifacts were produced.

## Exact artifacts

| Cell | Artifact id | ZIP digest | JSON SHA-256 |
| --- | ---: | --- | --- |
| EURUSD 5m | 10941671328 | `sha256:1044e35a44834c3ae93498d44e8824d462ae2627a7978d459ddf06ad711f46c9` | `17f972dab7435ef4790c98b97bc8e1e2c220454da0bf1112d7a091c7438640dc` |
| EURUSD 15m | 10941094396 | `sha256:28ede5e6cb5cf8a9a9caf6ba3ea2cedd7bb5371abe5393105ed37f6a933459ce` | `ea83442a7f9ab0710006d522247dbe0065990e8bbd59fc98fae8a695e68c9472` |
| EURUSD 1h | 10941517270 | `sha256:f53706c196f1646e3f8c4d89df893db7ba24d55e62ebed5e8ef12b99ce54a5d3` | `eba299f5995df7c068803197a8798789d3686fe53d7a99e83e4e4163714a3dfd` |
| GBPUSD 5m | 10940808485 | `sha256:85c328e46bee232ead82a4b56d65462bab65d9aa3c922143a2f9f8ea08008983` | `875bdadbc582d2fd20dbad50873f6310c1f41ff55f0b02c7622be3fa5ebe76ba` |
| GBPUSD 15m | 10941502297 | `sha256:998767ceab7f6b61998ef115c4ac58a2616294251c52a9098ea3be279c026cbd` | `ec8a62eff6363498a025766ba99f6c6b37385bf00fd38e09e162b9ef449f0f01` |
| GBPUSD 1h | 10941517129 | `sha256:b11fda55aba34b7343f825fbc8ffcff76ba5cc4842b67ca194763f4df6f00aca` | `159cf2f9b2b09bace8e20b26f1a6204d92e7f67de36e98dcabb6f17a88c2dd18` |
| USDJPY 5m | 10940628528 | `sha256:87040beea532b66f75e1cc387f68c2a0acd7e53ab1879714fba7abd42fd8fcfa` | `cfcab5225f384aaef89f330910fc238c2528a5f8d7c561c09a011920c823891f` |
| USDJPY 15m | 10941695816 | `sha256:f27155332639932241527f902bbf11bcf1adc71f00eb55be68e74ee915fe9f32` | `0d53fa4ef0ffbbb4e2c10cc4b73b32646382174877c686a8ce80c93010f64ec0` |
| USDJPY 1h | 10940793448 | `sha256:d4649d05f44d4ac5d512aeaf50b8b762b92e18025a4c71dc6cfc959cfea58ab9` | `a3f387c5352f01c978cacdbcd4290aba919db9aef27acb8999ee6bfe205a68a2` |
| aggregate | 10941770676 | `sha256:ce22fba00e711ba91f29c797dba19814aea9b9c907df66e8bfd75aefdcc08e5b` | `8f11806a4d2ffc4fb00a62360b35fc132efbb7f4e1ab44ea03a2244003dec056` |

The independently downloaded ZIPs hash to the same GitHub digests.

The nine downloaded `probe.json` objects exactly equal the nine cells stored in the downloaded aggregate proof.

## Deterministic content review

DEC-297 applies the predeclared DEC-295 terminal review and DEC-296 content review.

Verified totals:

- feature rows: `3,576,519`;
- outcome rows: `7,152,783`;
- real raw non-finite continuous feature values: `6,763`;
- `realized_vol_1h`: `2,683`;
- `realized_vol_8h`: `4,070`;
- `realized_vol_24h`: `10`;
- all other continuous features: `0` non-finite values.

All nine cells preserved exact feature/outcome adaptation row parity.

The proof therefore verifies the DEC-293 repair on the exact accepted 2015-2022 artifacts.

Verified meaning:

`NONFINITE_MISSING_VALUES_NORMALIZED_WITHOUT_MINING`

This is **not** a market-pattern, candidate, or strategy result.

## Frozen implementation

Result-freeze source:

`src/fmp/discovery/exp062_adapter_proof_result_decision.py`

Git blob:

`18b7dde7eadf0f051a09fda04e648650bb270eb7`

Focused tests:

`tests/test_phase8a_exp062_adapter_proof_result_freeze.py`

Git blob:

`90a9104dd0069c9c010b3517d2baa27336ff86bd`

## Locks preserved

DEC-297 keeps false:

- historical discovery execution;
- discovery-result production;
- reserved 2023-2026 robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

Only after DEC-295/296/297 are green and merged may a new source-only EXP-062 historical execution slot be designed.

That future slot must be a **new** slot under EXP-062, separate from closed EXP-061, while preserving the unchanged DEC-270 discovery/confirmation/validation semantics and keeping 2023-2026 reserved data and all candidate/trading paths locked.
