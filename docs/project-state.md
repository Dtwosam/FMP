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

## Recovery accounting audit — MERGED / LIVE-VALIDATED

PR #15 added `docs/phase1-recovery-accounting-audit.sql` and merged to `main` at:

- `83e7cce46833b4f8ab6224e9bec4f8ae8d1ba547`

The audit relies only on enforced acquisition/mirror invariants:

- a complete result mirrors **raw first, then manifest**;
- a `not_found` result mirrors **manifest only**;
- cloud objects are immutable and are not deleted to make accounting pass.

Therefore, once raw-only objects and unexpected paths are zero, planned manifest-only objects are the accounting class `manifest_only_inferred_not_found`. This is acquisition accounting only; Python provenance verification remains a separate required gate.

Live validation at `2026-09-09T11:26:49.677Z`:

- expected manifests: **25,500**
- present manifests: **24,520**
- missing manifests: **980**
- raw-backed manifests: **24,520**
- manifest-only inferred `not_found`: **0**
- raw without manifest: **3**
- unexpected manifest paths: **0**
- unexpected raw paths: **0**
- accounting gate: **FAIL**, correctly, because coverage/integrity are incomplete

Pair/side missing counts in that audit:

- EURUSD ASK: **32**
- EURUSD BID: **29**
- GBPUSD ASK: **153**
- GBPUSD BID: **154**
- USDJPY ASK: **309**
- USDJPY BID: **303**

The three raw-only objects were identified exactly:

- `raw/dukascopy/v1/GBPUSD/2020/05/01/BID_candles_min_1.bi5`
- `raw/dukascopy/v1/USDJPY/2015/08/03/ASK_candles_min_1.bi5`
- `raw/dukascopy/v1/USDJPY/2022/11/17/BID_candles_min_1.bi5`

Each maps to a planned manifest that is currently absent. Normal month/exact-gap repair will safely re-fetch the source chunk, receive `already_verified` for the immutable raw object if bytes match, then store the missing manifest. No raw deletion or overwrite exception is required.

## Final Phase 1 cloud-provenance + acceptance tooling — MERGED / READY

The final read-only provenance and cross-report acceptance path is now implemented without changing Dukascopy acquisition semantics.

Merged components:

- PR #16, merge `56fb8bc9639c081b62866d5417149a31d09b695b`: separate read-only `fmp-raw-audit` Supabase Edge Function source added; it remains **undeployed** while acquisition is active/incomplete.
- PR #17, merge `f16ab31e193ac93747e522507cb9c3c3acede595`: full cloud manifest/raw provenance verifier plus manual final cloud-audit workflow.
- PR #18, merge `d92e10537cab8dcb862558c5ff2a6415b524970b`: deterministic final Phase 1 acceptance combiner and runbook.

The provenance report now includes a canonical SHA-256 fingerprint of the exact planned pair/date/side key set. The frozen Phase 1 plan fingerprint is:

- `2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6`

This closes a fail-closed identity gap: a provenance report with merely 25,500 chunks is insufficient; its exact planned-key fingerprint must match the frozen V1 snapshot before final acceptance can pass.

Verification evidence for the fingerprint hardening:

- RED Actions run `34348884782` failed exactly because the provenance report lacked `plan_sha256` and the combiner accepted an intentionally wrong fingerprint;
- GREEN Actions run `34348988473` passed after the minimal implementation;
- merge-push unit-test run `34349117225` passed;
- no-source golden/network jobs were skipped as intended;
- the existing repair sweep 2 source job remained active and was not cancelled by the merge.

Final acceptance remains locked until acquisition is idle and the structural/accounting ledger is complete. Only then may the read-only audit Edge be deployed and the manual full cloud-provenance workflow run according to `docs/phase1-final-acceptance-runbook.md`.

## Final cloud-audit active-run guard — FIXED

PR #19 `[phase1-no-source] Phase 1: block all active acquisition states in final audit` merged to `main` at:

- `69d5075a0b42a0ebb7fba630b1ff2a0b719dd4c5`

The manual final cloud-provenance workflow previously queried only Phase 1 acquisition runs with `status=in_progress`. That was weaker than the final acceptance runbook, which requires no acquisition workflow to be queued, waiting, pending, or in progress before the cloud snapshot is treated as stable.

The guard now queries GitHub server-side for each active state — `queued`, `waiting`, `pending`, and `in_progress` — and refuses the audit when any such acquisition run exists. Server-side status queries are used rather than scanning only a bounded page of recent runs, so an older queued sweep cannot be missed after later CI activity.

Verification evidence:

- RED run `34349392546` failed exactly because the workflow still used the old single-status guard;
- GREEN run `34349499066` passed after the minimal workflow change;
- golden/network source jobs were skipped under `[phase1-no-source]`;
- no Supabase function was deployed and no new Dukascopy source traffic was introduced by this change.

## Final acceptance evidence identity/counter hardening — MERGED / VERIFIED

Two additional source-free fail-closed acceptance defects were closed while repair sweep 2 remained the only Dukascopy source workload.

### Structural evidence snapshot identity

PR #20 `[phase1-no-source] Phase 1: bind structural evidence to frozen snapshot` merged at:

- `aa9e6dfb9ab4e29d6f760042f4869bd20ec4854e`

Changes:

- `docs/phase1-final-acceptance-audit.sql` now emits:
  - `report_version = 1`;
  - `scope = phase1_structural_acceptance`;
  - `frozen_start_date = 2015-01-01`;
  - `frozen_end_date_exclusive = 2026-08-21`.
- the final acceptance combiner requires those identity fields to match the frozen snapshot.

Verification:

- RED run `34349685588` failed because structural identity was absent and a wrong frozen end date was accepted;
- GREEN run `34349752285` passed after the minimal implementation;
- the modified structural SQL was executed read-only against live Supabase at `2026-09-09 12:13:29.64728+00` and returned the expected identity fields while correctly keeping `structural_gate_pass = false` at 24,521 / 25,500 manifests.

### Provenance issue subcounter consistency

PR #21 `[phase1-no-source] Phase 1: validate provenance issue counters` merged at:

- `4b6ca4503dec7e705de9f31f7d51140c870ce41f`

The final acceptance combiner now independently requires zero for each provenance issue class:

- `invalid_manifest`;
- `raw_checksum_mismatch`;
- `raw_size_mismatch`;
- `invalid_raw_audit`.

This prevents a malformed or manually edited provenance report from passing merely because aggregate `issues = 0` and `ready = true` claim cleanliness.

Verification:

- RED run `34349955332` proved a nonzero `raw_checksum_mismatch` could previously be hidden by inconsistent aggregate fields;
- GREEN run `34350032666` passed after explicit subcounter checks were added;
- network/golden source checks skipped under `[phase1-no-source]`.

## Final cloud-provenance snapshot stability — MERGED / VERIFIED

PR #22 `[phase1-no-source] Phase 1: fail final audit on concurrent acquisition` merged to `main` at:

- `cbf9dc376cae4ebda1150d7eba2d1785ffef4d24`

The final 25,500-key cloud provenance workflow previously verified that Phase 1 acquisition was idle only before the audit began. Because `phase1-final-cloud-audit` and `phase1-full-acquisition` use separate concurrency groups, a full/repair/exact-gap acquisition run could otherwise begin while provenance verification was already scanning the cloud snapshot.

The workflow now:

- rejects any queued/waiting/pending/in-progress `phase1-full-acquisition` run before verification;
- records the latest acquisition workflow run ID as the audit baseline;
- re-reads that latest run ID after the full provenance scan and fails if it changed, catching even an acquisition that starts and finishes during verification;
- stamps `phase1-cloud-provenance.json` with `acquisition_baseline_run_id` and `acquisition_unchanged_during_verification = true` only after the post-verification stability check passes;
- keeps artifact upload fail-safe, but the final acceptance combiner now rejects provenance evidence unless the stability stamp and a valid baseline run ID are present.

This deliberately does not share the acquisition concurrency group: GitHub concurrency permits only one pending run per group and a newer pending run can replace an older one, so using a shared group for the audit could disturb legitimate recovery scheduling.

Verification evidence:

- RED run `34350773788` failed because the workflow lacked the run-ID stability guard;
- workflow guard GREEN run `34350844521` passed;
- RED run `34350929083` proved the final combiner still accepted provenance whose acquisition-stability stamp was false;
- final GREEN run `34351058998` passed after binding the stamp into the acceptance gate;
- docs-head GREEN run `34351121434` passed;
- golden/network source jobs skipped under `[phase1-no-source]`;
- no Supabase function was deployed and no Dukascopy source acquisition was started by this work.

## Pair/side accounting acceptance — MERGED / VERIFIED

PR #23 `[phase1-no-source] Phase 1: validate accounting pair-side evidence` merged to `main` at:

- `4e9e71ac1d875a8150f6dc5a12787a0c2fae157e`

The recovery/accounting SQL has always emitted a six-row `pair_side_breakdown`, but the final acceptance combiner previously trusted only aggregate totals. A malformed artifact could therefore omit or duplicate pair/side rows while retaining passing grand totals.

The final combiner now requires exactly one row for every frozen pair/side:

- EURUSD ASK/BID;
- GBPUSD ASK/BID;
- USDJPY ASK/BID.

Each row must contain exactly 4,250 expected and present manifests, zero missing manifests, zero raw-without-manifest objects, and a raw-backed + inferred-not-found partition of exactly 4,250. The six row-level raw-backed/not-found counts must also reconcile exactly to the accounting totals.

Verification evidence:

- RED run `34351355133` failed on both missing-breakdown and duplicate-row cases;
- GREEN run `34351433652` passed after the strict validator was added;
- docs-head GREEN run `34351492926` passed;
- golden/network source jobs skipped under `[phase1-no-source]`;
- no Dukascopy source acquisition or Supabase deployment was introduced by this change.

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
