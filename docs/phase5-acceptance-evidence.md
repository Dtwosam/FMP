# Phase 5 Leakage-Safe Feature Engine — Acceptance Evidence

**Review date:** 2026-09-15
**Result:** PASS
**Decision:** DEC-030 — APPROVED
**Checkpoint:** `fmp-v1-phase5-features` — CREATED at `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`
**Final-test touched?: NO**

## Acceptance gate

The approved build order defines Phase 5 PASS when feature datasets are versioned/reproducible and leakage tests cover all promoted feature families. DEC-029 further freezes acceptance to exactly 3 pairs × 3 timeframes = 9 source-free generation cells over 2015-01-01 through 2023-12-31, with reproducible manifests/digests and unchanged repository-wide regression surfaces.

The gate is satisfied.

## Authoritative implementation and regression evidence

- implementation PR: #102 — `[phase1-no-source] Implement Phase 5 leakage-safe feature engine`
- merged implementation SHA: `74dce1b945ad31a05416a4fc9e63443a884cb90c`
- merged-main tests run: `34910118880` — SUCCESS
- merged-main Phase 3 acceptance run: `34910118886` — SUCCESS
- implementation suite before merge: 509/509 tests PASS; workflow YAML PASS; compile PASS
- accepted feature schema: `fmp-feature-v1`, 55 columns total = 7 identity columns + 48 feature values
- accepted matrix: EURUSD / GBPUSD / USDJPY × 5m / 15m / 1h
- source coverage: 2015-01-01 through 2023-12-31 only
- normal Phase 5 tooling rejects source requests before 2015-01-01 and rejects any request reaching 2024-01-01 or later before opening a processed partition

No automatic Phase 5 generation ran on the implementation merge. The acceptance workflow remained manual-only.

## Authoritative Phase 5 generation run

Workflow `phase5-features` run `34910227756` was dispatched against exact merged-main SHA `74dce1b945ad31a05416a4fc9e63443a884cb90c` and completed **SUCCESS**.

All **9/9** matrix jobs succeeded. In every job the workflow:

1. downloaded the accepted immutable Phase 2 processed artifact;
2. verified both the accepted outer artifact ZIP SHA-256 and the accepted processed-manifest SHA-256;
3. generated the complete feature artifact set twice;
4. verified byte-identical deterministic regeneration and the locked pre-2024 coverage boundary; and
5. uploaded one evidence artifact for independent review.

| Symbol | Timeframe | Artifact ID | GitHub / independently recomputed ZIP SHA-256 | Rows |
| --- | --- | ---: | --- | ---: |
| EURUSD | 5m | `10374586073` | `4ea4d84d73346b217c990d8f088a8d35bfae4764fb41ada24f93ddc2b3337575` | 946,655 |
| EURUSD | 15m | `10374157583` | `d128440ba1b4b601da93d3055ed311a74da7c09fe783e2a78cee62bff2b0ba51` | 315,551 |
| EURUSD | 1h | `10373408888` | `294f63f35bfed673c7b620159f37de41370d5fcfcd44aab797a33f7a5505c854` | 78,887 |
| GBPUSD | 5m | `10374132726` | `fe7e3e28b6c741b4eaca9732e95beb3388ddf4d7bf2be85782b13aacf9fccc91` | 946,655 |
| GBPUSD | 15m | `10373129417` | `493194466e654475e5af3aaae7232deac8b0249d5baf62ca3910a5e9c436a933` | 315,551 |
| GBPUSD | 1h | `10374386463` | `5562431fd0bbfa98dfc6457a5e33c36815f119b7f8a9a719b6f57ef9309fa09d` | 78,887 |
| USDJPY | 5m | `10374615913` | `3c71f5cc759a97e7a89e99de322d4db96ef1eeaaad0140defd346cacc9de2789` | 946,655 |
| USDJPY | 15m | `10374600839` | `2e9b19935fc2699c94e5c3b91675c332892da9448e994438e479cf501e3c6215` | 315,551 |
| USDJPY | 1h | `10374645600` | `3db4d9d4fd4613c9e91f4c3fc1d815750038e33ea993608513066cec53aa617f` | 78,887 |

Total accepted generated rows across the nine cells: **4,023,279**.

## Accepted Phase 2 source identities

Every cell binds the corresponding accepted Phase 2 processed-manifest SHA-256:

- EURUSD: `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`
- GBPUSD: `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`
- USDJPY: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`

Every evidence manifest records generation parameters exactly `requested_start = 2015-01-01` and `requested_end_exclusive = 2024-01-01`.

## Independent artifact audit

All nine workflow artifacts were downloaded independently after the run completed. The audit did not rely on the generation workflow's internal comparison result.

Across the nine ZIPs:

- 9/9 downloaded ZIP SHA-256 values match the GitHub artifact digests shown above;
- exactly 972/972 monthly Parquet partitions are present and declared: 108 months per cell from 2015-01 through 2023-12;
- 972/972 independently recomputed inner Parquet SHA-256 values match their evidence manifests;
- 972/972 file sizes match their evidence manifests;
- 972/972 Parquet-footer row counts match their evidence manifests;
- all 972 partitions expose one identical 55-column Parquet schema matching the evidence manifest schema list;
- every cell reports exactly 48 feature columns and 48 corresponding per-feature null-count entries;
- every cell reports `row_count == unique_key_count`;
- no evidence ZIP contains a 1m feature path;
- no evidence ZIP contains a 2024-or-later feature path;
- all opened-source month lists are exactly 108 months, 2015-01 through 2023-12;
- all output coverage ends before 2024-01-01.

Output coverage by timeframe is consistent across all three symbols:

- 5m: 946,655 rows; first bar 2015-01-01T00:00:00Z; final `bar_end_utc` 2023-12-31T23:55:00Z
- 15m: 315,551 rows; first bar 2015-01-01T00:00:00Z; final `bar_end_utc` 2023-12-31T23:45:00Z
- 1h: 78,887 rows; first bar 2015-01-01T00:00:00Z; final `bar_end_utc` 2023-12-31T23:00:00Z

The artifact audit found **zero validation errors**.

## Leakage and boundary verification

The accepted implementation regression suite covers:

- prefix equivalence;
- future perturbation invariance;
- current-closed-bar allowance;
- exact-cadence and incomplete-bar null semantics;
- post-gap warm-up behavior;
- DST-aware Tokyo, London, and New York session membership;
- U.S./U.K. DST-mismatch overlap behavior;
- completed-reference-only Asia/London and New-York-close market-location levels;
- deterministic regeneration;
- exact frozen schema and feature dictionary agreement;
- source path/manifest/hash guards before Parquet reads;
- pre-2015 rejection before manifest/data access;
- hard final-test rejection before any 2024+ processed partition open;
- writer rejection of 2024+ output and processed-manifest identity mismatch;
- manual-only, source-free nine-cell workflow constraints.

The authoritative run touched only accepted Phase 2 processed artifacts through 2023-12. The final untouched 2024-01-01 through 2026-08-20 partition was not read or generated into Phase 5 features.

## Scope and lock verification

Phase 5 introduced no:

- 1m feature matrix;
- cross-pair or multi-timeframe feature joins;
- relative source-activity family;
- labels, targets, model fitting, or target-driven feature selection;
- strategy/candidate retuning;
- Phase 6 model experiment;
- broker/live/demo integration;
- real-money capability or permission.

The two frozen Phase 4 serious research candidates remain unchanged.

## Acceptance conclusion

Phase 5 satisfies DEC-029 and the approved build-order acceptance gate and is ready to close as **PASS**.

The acceptance closure merged at `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`. Post-merge tests run `34912677109` and Phase 3 acceptance run `34912677100` both completed SUCCESS, and no Phase 1 acquisition ran. Checkpoint `fmp-v1-phase5-features` was then created at that exact verified closure commit.

This acceptance does **not** authorize Phase 6 implementation, final-test inspection, broker/live/demo integration, or real-money trading. Those remain separate later gates.
