# FMP Project State

**Updated:** 2026-09-09  
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 1 — Historical Data Acquisition  
**Phase status:** REPAIR_SWEEP_2_ACTIVE  
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

## Chunk-level source-failure isolation + serial repair batch — MERGED / ACTIVE

PR #10 was completed and merged after the first serialized full-history pass stopped.

Merged behavior:

- terminal Dukascopy `AcquisitionError` can be isolated to one chunk with `--continue-on-error`;
- later source chunks continue after a terminal source acquisition failure;
- cloud/OIDC/Supabase mirror failures remain fail-fast;
- monthly provenance verification remains fail-closed;
- targeted month repair and a queue-driven serial repair batch are available;
- repair batches use the same one-source-runner, 8-attempt, 5-second pacing policy.

Repair sweep 1 trigger:

- `a8d9467f6ae4a46d2e71c0646b63ed2485e76f7e`

Repair sweep 1 result after the full 121-month queue completed:

- expected manifests: **25,500**
- present manifests: **24,080**
- missing manifests: **1,420**
- coverage: **94.4314%**
- raw objects: **24,085**
- raw-only objects: **5**
- complete calendar months: **66 / 140**
- months with one or more remaining gaps: **74**
- no repair jobs remained active or queued after the sweep completed.

The five raw-only objects at the sweep-1 audit were preserved and will be reconciled by later repair/audit passes; they are not deleted or overwritten.

Repair sweep 2 was generated directly from the exhaustive post-sweep gap audit:

- queue revision: **2**
- queue size: **74 months**
- missing manifests at trigger: **1,420**
- trigger commit: `3bbca039ea5a9ce6c5a27f8e50b9abaa5b09d2b2`
- trigger message: `chore: start Phase 1 repair sweep 2 [phase1-repair-batch]`
- queue validation: PASS
- unit tests on trigger commit: PASS
- cloud smoke/full acquisition/targeted repair jobs: correctly skipped for the batch trigger
- first active repair month: **2015-02**
- remaining 73 repair months queued behind it under `max-parallel: 1`.

Phase 1 remains open until exhaustive coverage reaches 25,500/25,500 and final integrity/provenance gates pass.

## Exact-gap sparse cleanup tooling — MERGED / READY

PR #12 `[phase1-no-source] Phase 1: add exact-gap repair path` was merged to `main` at:

- `a6bf7e2ecf215cf65e99cc9653267abe9ddb4eb1`

Purpose: eliminate the large replay overhead of month-level repair once remaining gaps become sparse.

Merged behavior:

- `docs/phase1-exact-gap-audit.sql` deterministically emits the exact missing pair/date/side plan from the frozen 25,500-manifest target;
- exact-gap plan root schema is strict and includes:
  - frozen start/end boundaries,
  - UTC audit timestamp,
  - present/missing manifest counts,
  - exact chunk list;
- audit counts must reconcile to exactly **25,500** and declared missing count must equal the chunk list length;
- duplicate, unsupported, out-of-range, unknown-field, and non-canonical plans fail closed;
- chunk order is canonical by date / pair / side;
- `fetch-plan` requests only explicit chunks from the validated plan;
- `verify-plan` verifies provenance only for the explicit sparse plan;
- exact-gap execution preserves the existing one-runner / 8-attempt / 5-second Dukascopy policy;
- acquisition errors may continue to later exact chunks, while cloud/OIDC/Supabase failures remain fail-fast;
- `[phase1-exact-gap-batch]` is the dedicated sparse-repair trigger;
- exact-gap GitHub reruns are rejected: after any partial/failed sparse pass, a **fresh Supabase audit and fresh exact-gap plan are required**;
- `[phase1-no-source]` suppresses all push-triggered Phase 1 acquisition jobs and also suppresses PR golden/network source tests for code-only changes;
- `docs/phase1-final-acceptance-audit.sql` codifies the final structural cloud acceptance query.

Verification evidence:

- exact-gap implementation followed RED -> GREEN tests;
- unit-test suite + package compilation PASS on the final PR head;
- tests prove invalid plans fail before any acquisition attempt;
- tests prove valid sparse execution attempts only the explicit keys in plan order;
- ready-for-review golden/network Dukascopy jobs were both **skipped** under `[phase1-no-source]`;
- merge push used `[phase1-no-source]`;
- the existing repair sweep 2 remained the only active Dukascopy acquisition run after the merge.

Latest cloud sample recorded during this documentation update:

- manifests: **24,520 / 25,500**
- coverage: **96.1569%**
- remaining manifests: **980**
- raw objects: **24,523**
- latest manifest write in that sample: `2026-09-09 09:18:39.532127+00`

This sample is progress evidence only. The exact-gap workflow has **not** been triggered yet.

## Live validation of committed Phase 1 audit tooling — PASS

The committed audit queries were executed directly against the live dedicated FMP Supabase project after merge of the exact-gap tooling.

### Exact-gap audit integration

`docs/phase1-exact-gap-audit.sql` executed successfully and emitted the strict schema consumed by `load_exact_gap_plan`:

- plan version: **1**
- frozen start: **2015-01-01**
- frozen exclusive end: **2026-08-21**
- audit timestamp: **2026-09-09T11:11:59.752Z**
- present manifests at audit: **24,520**
- missing manifests at audit: **980**
- exact missing chunk list: **980 pair/date/side keys**

The returned list is canonical by date / pair / side and the declared counts reconcile to the frozen **25,500** target. This is integration evidence only; the output was not materialized as the active exact-gap queue because repair sweep 2 is still running and the plan would become stale.

### Final structural acceptance audit integration

`docs/phase1-final-acceptance-audit.sql` also executed successfully against the live ledger:

- expected manifests: **25,500**
- present manifests: **24,520**
- missing manifests: **980**
- completion: **96.1569%**
- raw objects: **24,523**
- unexpected manifest paths: **0**
- raw without matching manifest: **3**
- unexpected raw paths: **0**
- latest manifest write: `2026-09-09 09:18:39.532127+00`
- structural gate: **FAIL**, as required while coverage/integrity are incomplete

The false structural result is expected and proves the gate does not incorrectly declare Phase 1 complete while manifests are missing or raw-only objects remain.

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

1. Allow repair sweep 2 to continue under the existing single-source-runner lock; do not add parallel Dukascopy traffic.
2. When sweep 2 stops, run the committed exhaustive cloud audit against the exact **25,500-manifest** frozen plan.
3. If missing manifests remain, materialize `docs/phase1-exact-gap-queue.json` directly from `docs/phase1-exact-gap-audit.sql`.
4. Trigger one `[phase1-exact-gap-batch]` sparse pass. Do **not** rerun the same workflow attempt after partial success/failure.
5. After every sparse pass, generate a fresh cloud audit and fresh exact-gap plan from only still-missing chunks.
6. Continue bounded exact-gap audit/repair cycles until missing manifests reach zero.
7. Reconcile any remaining raw-only objects through immutable/idempotent repair semantics; never delete cloud raw data to make counts match.
8. Run `docs/phase1-final-acceptance-audit.sql` plus the required provenance/recovery-accounting checks.
9. Record Phase 1 PASS/checkpoint only after **25,500 / 25,500** and all integrity gates are proven.
10. Keep Phase 2 locked until that PASS is recorded.

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
