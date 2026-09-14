# FMP Decision Log

Later approved decisions override older assumptions only when this log says so and affected source-of-truth files are updated in the same change.

The complete detailed text of DEC-001 through DEC-013 is preserved in the immutable pre-PASS repository state at commit `0ff45220cd930839059afcfba631e1e120cb38aa`, path `docs/decision-log.md`. Those detailed rules remain authoritative whenever a historical Phase 1 acquisition or integrity-repair rule is relevant.

Active decision index:

- DEC-001 — Forex-only V1 — APPROVED
- DEC-002 — $0 development constraint — APPROVED
- DEC-003 — Python-owned trading engine — APPROVED
- DEC-004 — Canonical 1-minute bid/ask data — APPROVED
- DEC-005 — Initial historical data source candidate — SUPERSEDED BY DEC-009
- DEC-006 — Simpler model wins ties — APPROVED
- DEC-007 — Backtester before strategy benchmarking — APPROVED
- DEC-008 — Real-money lock — APPROVED
- DEC-009 — Phase 1 Dukascopy retrieval method — APPROVED
- DEC-010 — Dedicated Supabase raw snapshot persistence — APPROVED
- DEC-011 — Serialize and monthly-isolate Dukascopy acquisition — APPROVED
- DEC-012 — Sparse exact-gap Phase 1 cleanup and acceptance safety — APPROVED
- DEC-013 — No in-place cloud promotion of canonical `not_found` manifests — APPROVED
- DEC-014 — Phase 1 frozen snapshot accepted — APPROVED
- DEC-015 — Phase 2 exhaustive acceptance review — APPROVED, CHECKPOINT PENDING

## DEC-014 — Phase 1 frozen snapshot accepted

**Date:** 2026-09-13  
**Status:** APPROVED

Phase 1 is formally accepted for the frozen Dukascopy V1 snapshot covering 2015-01-01 through 2026-08-20 inclusive for EURUSD, GBPUSD, and USDJPY with separate BID and ASK 1-minute acquisition.

Acceptance evidence:

- structural ledger audit `2026-09-13T12:54:55.900Z`: 25,500 expected, 25,500 present, zero missing, zero unexpected manifest paths, zero raw-without-manifest, zero unexpected raw paths;
- recovery/accounting audit `2026-09-13T12:55:12.135Z`: 25,500 raw-backed manifests, zero inferred `not_found`, all six pair/side buckets exactly 4,250/4,250, accounting gate PASS;
- final cloud provenance run #4 / `34758527971` on head `0ff45220cd930839059afcfba631e1e120cb38aa`: 25,500 planned and complete, zero invalid manifests, zero invalid raw audits, zero checksum mismatches, zero size mismatches, zero issues, `ready = true`;
- frozen plan SHA-256 `2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6`;
- acquisition baseline run `34718347187`, completed `2026-09-12T21:23:53Z`;
- provenance history guard start `2026-09-13T12:58:28.353525Z`, with acquisition unchanged during verification;
- cross-report acceptance: 55 checks passed, 0 failed.

Consequences:

- Phase 1 status is PASS.
- Phase 2 — Validation, Normalization & Derived Bars — is unlocked and may begin.
- Phase 1 acceptance proves acquisition completeness and cloud provenance only; quote cleanliness, market-session interpretation, gap classification, normalization, and 5m/15m/1h derived-bar correctness remain Phase 2 responsibilities.
- No further Phase 1 acquisition or repair is required for the frozen snapshot unless later evidence demonstrates an integrity defect.
- DEC-008 remains unchanged: real-money trading remains locked pending a later explicit approval.

## DEC-015 — Phase 2 exhaustive acceptance review

**Date:** 2026-09-14  
**Status:** APPROVED, CHECKPOINT PENDING

The exhaustive Phase 2 evidence for EURUSD, GBPUSD, and USDJPY satisfies the acceptance gates in `docs/build-order.md` and `docs/data-spec.md`.

Acceptance evidence:

- `phase2-full-history` run `34782357048` on head `158c1c121655867b7fb2886fe755585dfcd682ec` completed successfully on attempt 2;
- each pair covers 2015-01-01 through 2026-08-20 inclusive with exactly 8,500 verified reads, 140 calendar months, and 140 monthly partitions for each of 1m/5m/15m/1h;
- each pair produced 6,120,000 1m rows, 1,224,000 5m rows, 408,000 15m rows, and 102,000 1h rows;
- each pair has a versioned processed manifest containing 561 artifacts;
- independent artifact inspection found zero digest, size, ledger-identity, or monthly-partition validation errors;
- all three quality reports show zero duplicate rows, zero missing BID/ASK rows, zero required nulls, zero missing open-market minutes, and zero suspicious gaps;
- outlier observations remain recorded as telemetry and were not silently removed or rewritten;
- the required canonical, quote-sanity, duplicate/missing timestamp, resampling boundary, weekend-gap, DST, ledger, workflow-guard, and materialization tests were green on the merged implementation and post-merge main CI.

The initial USDJPY job received one HTTP 401 from the read-only raw Edge Function. Rerunning only that job without code, data, source, or configuration changes succeeded; the authentication failure did not reproduce and is not treated as a deterministic data or materialization defect.

Consequences:

- Phase 2 acceptance review is PASS.
- Formal Phase 2 status remains checkpoint-pending until checkpoint `fmp-v1-phase2-normalized-data` is recorded if checkpoints use Git tags/refs.
- Phase 3 remains unstarted.
- DEC-008 remains unchanged; this decision does not authorize real-money trading.
- Detailed evidence is recorded in `docs/phase2-acceptance-evidence.md`.
