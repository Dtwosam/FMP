# FMP Project State

**Updated:** 2026-08-22  
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 1 — Historical Data Acquisition  
**Phase status:** SERIALIZED_MONTHLY_RECOVERY_ACTIVE  
**Next phase:** Phase 2 — Validation, Normalization & Derived Bars (LOCKED until Phase 1 PASS)

## Current baseline

- Instruments: EUR/USD, GBP/USD, USD/JPY
- Canonical history: 1-minute bid/ask
- Derived bars: 5m, 15m, 1h
- Frozen first snapshot target: 2015-01-01 through 2026-08-20 inclusive
- Planned pair/side/date manifests: **25,500**
- Development budget: $0
- Historical source: Dukascopy daily M1 BID/ASK `.bi5`, frozen by DEC-009
- Phase 1 persistent cloud copy: dedicated Supabase `FMP` project, private `fmp-raw` bucket, frozen by DEC-010
- Phase 2+ research storage: Parquet + DuckDB outside the Phase 1 raw bucket
- Language: Python
- ML: optional, only after baselines
- Execution choice: deferred until demo/shadow needs justify it
- Real-money trading: locked

## Phase 0 — PASS

**Merge commit:** `31cd8decca5dcb90f9d123ff33f71ac20413e269`  
**Checkpoint ref:** `fmp-v1-phase0-source-of-truth`

All Phase 0 source-of-truth, architecture, data, research, risk, build-order, experiment-log and continuation-rule gates are complete.

## Phase 1 — completed foundation gates

### Source/acquisition
- [x] deterministic Dukascopy daily M1 BID/ASK source adapter
- [x] resumable local acquisition semantics
- [x] atomic raw/manifest writes
- [x] SHA-256 provenance
- [x] fail-closed tamper handling
- [x] structural LZMA/record validation
- [x] explicit 404 `not_found` provenance
- [x] delayed-404 recheck path
- [x] transient 5xx retry handling
- [x] acquisition coverage report
- [x] snapshot provenance verifier
- [x] all-pair golden sample PASS
- [x] retrieval method frozen as DEC-009

### Persistent cloud snapshot
- [x] dedicated Supabase `FMP` project created at verified `$0/month`
- [x] private `fmp-raw` bucket created
- [x] GitHub OIDC trust boundary implemented/tested
- [x] Supabase `fmp-raw-ingest` Edge Function deployed
- [x] canonical V1 object-path validation
- [x] SHA-256 required before storage
- [x] Python GitHub-OIDC mirror client
- [x] immediate per-result cloud mirroring
- [x] retry-manifest idempotency defect regression-tested, fixed, deployed as Edge Function v3 and merged via PR #5

## First full-history run — INCOMPLETE

Original trigger:

- `496ef145daf694902d09d17e5f969cc62a93fefd` — `chore: start Phase 1 full acquisition [phase1-full]`

Original workflow shape:

- 36 pair/year jobs
- maximum 3 concurrent source runners
- whole-year failure blast radius
- 6-attempt source retry budget
- no explicit inter-chunk source pacing

Independent Supabase audit after writes stopped:

- expected manifests: **25,500**
- present manifests: **1,055**
- missing manifests: **24,445**
- raw objects: **1,055**
- manifest objects: **1,055**
- total objects: **2,110**
- latest object from the stopped run: `2026-08-22 03:59:46.247262+00`

The partial cloud snapshot is valid persisted progress but is **not** Phase 1 completion evidence.

## Root cause — DUKASCOPY THROTTLING / SOURCE INSTABILITY

Diagnostic CI reproduced repeated Dukascopy HTTP 503 responses under the earlier three-runner concurrency.

- GitHub Actions run `32561119936`, USDJPY job `97002685840`: six retries exhausted on HTTP **503** for `USDJPY/2024/00/04/ASK_candles_min_1.bi5`.
- same run, GBPUSD job `97002685900`: six retries exhausted on HTTP **503** for `GBPUSD/2022/00/04/ASK_candles_min_1.bi5`.
- serial hypothesis run `32561495430`: both exact URLs later returned HTTP **200**; another serial request later received `Connection reset by peer`.

Conclusion: Dukascopy is load-sensitive and intermittently unstable. Supabase was not the primary cause.

## Recovery hardening — MERGED / VERIFIED

PR #7 `Phase 1: harden Dukascopy throttling recovery` merged to `main` at:

- `47e8d29cc9ef797e85817b8036cc8f8d876696fc`

TDD / verification evidence:

- red commit `b26306ceebcad10641ae4658a6d9179f21057aa1` added source-pacing requirements;
- CI failed exactly because those behaviors were absent;
- green implementation commit `619e8e5cb9dfec83e3e4d5b8d604799493be3072` added the minimal pacing support;
- Python suite passed all **20 tests**;
- all-pair golden sample PASS;
- strengthened six-day paced live Dukascopy smoke PASS, including acquisition, full bounded provenance verification and coverage.

Current recovery policy, frozen by DEC-011:

- `max-parallel: 1` source runner;
- calendar-month shards rather than pair/year shards;
- all three V1 pairs processed sequentially inside each active month;
- `--attempts 8`;
- `--source-delay 5` seconds;
- immediate Supabase mirroring after every acquisition result;
- local provenance verification after every monthly shard;
- failed months remain isolated and retryable;
- first snapshot remains capped at exclusive `2026-08-21`.

## Post-hardening cloud smoke — PASS

After PR #7 merged, a dedicated smoke-only main commit was issued:

- `c2db407b23b5a7f75469a275737ea066204f97a8` — `chore: trigger post-hardening Phase 1 cloud smoke`

Edge Function v3 recorded four fresh authenticated HTTP **200** idempotent PUT responses for the existing EUR/USD 2024-01-02 BID/ASK raw+manifest smoke objects. No 401/409 failure was observed.

## Serialized monthly recovery — ACTIVE

Recovery trigger:

- `a2fdeab9ed2bdca069c8f710ed3faf07915e3683` — `chore: start serialized Phase 1 recovery [phase1-full]`

Independent Supabase observation proves the recovery is filling previously missing history, not merely replaying smoke objects:

- `raw/dukascopy/v1/EURUSD/2015/00/01/BID_candles_min_1.bi5` stored at `2026-08-22 08:35:58.215815+00`;
- matching BID manifest stored at `2026-08-22 08:35:59.270894+00`;
- the stressed ASK request eventually recovered and stored its raw object at `08:38:52.364578+00` and manifest at `08:38:53.083381+00`;
- the worker then advanced to EUR/USD 2015-01-02 BID, storing raw at `08:39:09.440082+00` and manifest at `08:39:10.394765+00`.

This is direct live evidence that the hardened retry/pacing policy can survive multi-minute source stalls and continue to later chunks.

### January 2015 first-pair completion / pair handoff evidence

A later direct Supabase audit established the first complete pair/month under the hardened recovery:

- EUR/USD January 2015 reached **62/62** planned BID/ASK manifests;
- raw/manifest object parity remained exact;
- the same monthly worker then advanced into GBP/USD January 2015 without restarting or changing policy;
- at the latest state sample used for this ledger update, GBP/USD January had reached **8/62** manifests;
- USD/JPY January already contained **34/62** persisted manifests from the earlier partial run; those objects remain immutable/idempotent cloud progress, although a fresh runner still re-requests Dukascopy before the cloud mirror can return `already_verified`;
- global snapshot at that sample: **1,125 manifests / 1,125 raw objects**, zero raw/manifest delta;
- latest object timestamp in that sample: `2026-08-22 09:24:02.968782+00`.

This proves the monthly worker executes the intended serial pair loop (`EURUSD` → `GBPUSD` → `USDJPY`) and that the first pair completed without unexplained missing chunks.

These values are progress evidence only. Phase 1 remains open until the count reaches 25,500/25,500 and all remaining acceptance checks pass.

## Prepared source-failure isolation safeguard — DRAFT / NOT MERGED

Draft PR #10: `Phase 1: isolate terminal source failures to one chunk`

Purpose:

- reduce a future terminal Dukascopy failure from “rest of month skipped” to “one unresolved chunk remains absent”;
- continue attempting later source chunks only after `AcquisitionError`;
- preserve the existing monthly `verify` step as the fail-closed gate;
- keep cloud/OIDC/Supabase mirror failures fail-fast and never swallow them.

TDD evidence:

- RED commit `c1810972f0aea4045a2c327b67352328f7b2ecba`: existing tests passed; new tests failed exactly because `--continue-on-error` and chunk-level continuation were missing;
- GREEN implementation begins at `6235de930c4b15932f3af2a6a8c9e41fd9043205`;
- guard test at `1f702f2fe27d2a633bd433e3a0a83fa74042a4e0` proves continue mode does not swallow cloud mirror failures;
- latest unit-test workflow PASS and package compilation PASS;
- draft-PR network/golden workflows are configured to skip while PR #10 remains draft, avoiding unnecessary Dukascopy source contention.

Operational rule: **do not merge PR #10 while the active serialized recovery remains healthy merely because the fallback is green.** It is a prepared recovery safeguard if a monthly shard actually terminates after exhausted source retries.

## Manifest retry incident — FIXED

Current Edge Function v3 rule:

- raw `.bi5` objects remain strictly byte-for-byte immutable;
- duplicate manifest bytes are accepted directly when SHA-256 matches;
- when manifest bytes differ, semantic comparison ignores **only** top-level `retrieved_at_utc`;
- every other manifest field must match;
- first cloud manifest remains stored; retry attempts do not overwrite it;
- substantive conflicts still return HTTP 409.

Merged via PR #5 at commit `a2906a37f380dc6c4d27e90d46f15c2c2731d417`.

## Remaining Phase 1 gates

- [ ] serialized monthly recovery completes / all failed months retried
- [ ] all **25,500** planned pair/side/date manifests accounted for
- [ ] expected source-404 / market-closure manifests accounted for
- [ ] no unexplained missing planned chunks
- [ ] final cloud coverage/provenance evidence recorded
- [ ] Phase 1 acceptance gate recorded PASS
- [ ] Phase 1 checkpoint recorded

## Immediate next action

1. Allow the already-triggered serialized monthly recovery to continue using the proven 8-attempt / 5-second pacing policy.
2. Monitor GBP/USD January 2015 through completion and confirm handoff into USD/JPY within the same monthly job.
3. Do not change acquisition policy merely because a chunk is quiet during retries; repeated live stalls have recovered successfully.
4. Keep PR #10 draft/unmerged unless a monthly shard actually terminates and the prepared source-failure isolation safeguard is needed.
5. Re-audit the bucket against the exact 25,500-manifest plan after the matrix stops changing.
6. Retry only missing/failed monthly shards as needed; immutable/idempotent storage makes reruns safe.
7. Record final coverage/provenance evidence and Phase 1 PASS only after every planned chunk is accounted for.
8. Keep Phase 2 locked throughout recovery.

## Known open decisions

1. Exact chronological train/validation/final-test boundaries — Phase 2 data-quality dependent.
2. Exact intrabar ambiguity policy implementation details — Phase 3.
3. Exact demo broker/adapter — Phase 8/9.
4. Exact live capital/risk — outside current scope until Phase 10 review + Phase 11 approval.

## Backlog — do not pull forward

- economic-calendar/event-risk filter
- tick-level execution validation
- dashboard
- advanced multi-pair correlation controls
- alternative data
- broader cloud hosting beyond Phase 1 raw persistence
- live-money execution
- indices/crypto/gold/commodities
