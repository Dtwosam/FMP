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

## Final evidence freshness vs acquisition baseline — MERGED / VERIFIED

PR #24 `[phase1-no-source] Phase 1: bind final evidence to acquisition baseline time` merged to `main` at:

- `99fb8bcd6686e70d745288c2ecb3ed58754e247f`

The final acceptance combiner previously validated structural/accounting identities and provenance stability, but did not prove that the structural/accounting ledger reports were generated after the latest acquisition workflow used as the provenance baseline. A stale clean ledger report could therefore be paired with newer provenance evidence.

The final cloud-provenance workflow now records the latest completed `phase1-full-acquisition` workflow `updated_at` timestamp as `acquisition_baseline_completed_at_utc` alongside the baseline run ID. The final acceptance combiner requires:

- a valid timezone-aware acquisition baseline completion timestamp;
- a valid timezone-aware structural `audited_at_utc`;
- a valid timezone-aware accounting `audited_at_utc`;
- both ledger audit timestamps to be at or after the acquisition baseline completion timestamp;
- the existing acquisition-unchanged-during-verification stamp to remain true.

Verification evidence:

- RED run `34355560210` failed on stale structural evidence, stale accounting evidence, malformed baseline completion time, and missing workflow stamping;
- GREEN implementation run `34355687877` passed;
- docs-head GREEN run `34355823707` passed;
- golden/network source jobs skipped under `[phase1-no-source]`;
- no Dukascopy acquisition or Supabase deployment was introduced by this change.

## Final cloud-audit requested-state guard — MERGED / VERIFIED

PR #25 `[phase1-no-source] Phase 1: block requested acquisition runs in final audit` merged to `main` at:

- `256639d0d50996ac584de84b956fb1fe38e1de78`

GitHub Actions exposes `requested` as a non-completed workflow-run status in addition to `queued`, `waiting`, `pending`, and `in_progress`. The final cloud-audit precheck previously omitted `requested`.

The guard now rejects all five non-completed acquisition states before treating the cloud snapshot as stable:

- `requested`;
- `queued`;
- `waiting`;
- `pending`;
- `in_progress`.

Verification evidence:

- RED run `34356031188` failed exactly because the workflow omitted `requested`;
- GREEN implementation run `34356086024` passed;
- docs-head GREEN run `34356136210` passed;
- golden/network source jobs skipped under `[phase1-no-source]`;
- no Dukascopy acquisition or Supabase deployment was introduced by this change.

## Final cloud-audit baseline race guard — MERGED / VERIFIED

PR #26 `[phase1-no-source] Phase 1: require completed final-audit baseline` merged to `main` at:

- `9669152ef6ad40c3e3fb96f1589b12f848c873fc`

The final audit already rejected known active acquisition statuses before capturing its acquisition baseline, but there was still a race: a new acquisition run could be created after the status scan and before baseline capture. The latest run ID could then be captured from a non-completed run.

The baseline capture now reads one GitHub API response and validates the captured latest `phase1-full-acquisition` run atomically:

- a positive integer run ID is required;
- the captured run must itself have `status = completed`;
- the captured run must have a non-empty completion/update timestamp;
- only then are the baseline run ID and completion timestamp exported for provenance verification.

Verification evidence:

- RED run `34356363553` failed because the workflow did not validate the captured baseline status;
- first implementation commit `32453933ede64bf8a3db9a84c9fd40216081434c` exposed an invalid-workflow regression before merge; GitHub rejected `.github/workflows/phase1-final-cloud-audit.yml` in run `34356447055`;
- the workflow was restored from `main` and the atomic baseline capture was reimplemented safely at `8a760f92a7657e95a34be73f46a939361fab88a7`;
- final GREEN unit run `34356594966` passed;
- docs-head GREEN run `34356647166` passed;
- golden/network source jobs skipped under `[phase1-no-source]`;
- no Dukascopy source acquisition or Supabase deployment was introduced by this change.

## Workflow YAML syntax validation — MERGED / VERIFIED

PR #27 `[phase1-no-source] Phase 1: validate GitHub workflow YAML in CI` merged to `main` at:

- `64fb767328296a03d31ab5a2277e50e806a6c385`

The normal unit-test gate previously exercised workflow semantics with text assertions but did not syntax-parse every GitHub Actions YAML file. During PR #26 this allowed an intermediate malformed workflow commit to pass Python tests while GitHub separately rejected the workflow definition.

CI now includes a dependency-free Ruby/Psych validator:

- `scripts/validate_workflow_yaml.rb` syntax-parses every `.github/workflows/*.yml` / `.yaml` file;
- `tests/test_workflow_yaml_validation.py` proves all repository workflows parse and proves malformed YAML is rejected;
- `.github/workflows/tests.yml` runs workflow YAML validation before unit tests.

Verification evidence:

- RED run `34357268414` failed because the validator script did not yet exist;
- GREEN run `34357358399` passed the new `Validate workflow YAML syntax` step, unit tests, and compile step;
- golden/network source jobs skipped under `[phase1-no-source]`;
- no Dukascopy acquisition or Supabase deployment was introduced by this change.

## Exact-gap intervening-acquisition guard — MERGED / VERIFIED

PR #28 `[phase1-no-source] Phase 1: reject stale exact-gap plans after intervening acquisition` merged to `main` at:

- `d632046dfcbc245aaba62404d373819551e19da6`

Exact-gap plans already had strict frozen-snapshot validation and a two-hour freshness window, but age alone did not prove that the cloud ledger was unchanged after the plan audit. A different source-capable `phase1-full-acquisition` run could complete or partially write after the audit and before sparse execution, leaving a young but logically stale plan.

Before `fetch-plan` can access Dukascopy, the exact-gap workflow now:

- pages the full `phase1-full-acquisition` workflow history with GitHub Actions read permission;
- excludes the current exact-gap workflow run;
- excludes runs explicitly tagged `[phase1-no-source]`, because those jobs cannot access the source;
- treats all other runs conservatively as source-capable;
- rejects the plan if any such run has `updated_at` later than the plan's `audited_at_utc`, including failed/cancelled runs that may have partially mirrored data;
- persists `.phase1-exact-gap-run-guard.json` alongside the exact-gap plan and verification evidence.

DEC-012 and the Phase 1 acquisition trigger runbook now record that freshness-by-age is necessary but not sufficient: no intervening source-capable acquisition may exist after the audit.

Verification evidence:

- RED run `34363736380` failed on the absent helper and absent pre-source workflow guard;
- GREEN implementation run `34363945420` passed workflow YAML validation, unit tests, and compile;
- docs-head GREEN run `34364056475` passed;
- golden/network source jobs skipped under `[phase1-no-source]`;
- no Dukascopy acquisition or Supabase deployment was introduced by this change.

## Exact-gap manual-dispatch classification — MERGED / VERIFIED

PR #29 `[phase1-no-source] Phase 1: treat manual exact-gap predecessors as source-capable` merged to `main` at:

- `6dceb5191957e46f506827c58473378c4b9f7a16`

The intervening-acquisition guard added by PR #28 initially ignored any workflow run whose head commit message contained `[phase1-no-source]`. That classification is correct for push-triggered runs because all push acquisition jobs explicitly suppress source access under that tag, but it is not correct for manual `workflow_dispatch`: manual full/targeted acquisition can still run from a commit whose message happens to contain the tag.

The guard now:

- ignores `[phase1-no-source]` only when the workflow run event is `push`;
- continues to exclude the current exact-gap run;
- treats manual `workflow_dispatch` runs as source-capable regardless of the underlying head-commit message;
- therefore rejects a sparse plan if such a manual run was updated after the plan audit.

DEC-012 and the acquisition trigger runbook now state this push-only exemption explicitly.

Verification evidence:

- RED run `34364290527` failed exactly because a manual dispatch with a no-source head message was incorrectly ignored;
- GREEN run `34364388003` passed workflow YAML validation, unit tests, and compile;
- golden/network source jobs skipped under `[phase1-no-source]`;
- no Dukascopy acquisition or Supabase deployment was introduced by this change.

## Raw-only reconciliation fail-closed proof — MERGED / VERIFIED

PR #30 `[phase1-no-source] Phase 1: prove raw-only reconciliation fails closed` merged to `main` at:

- `fe361a3dad01a154f016b569e2832632e56f1d10`

The three known planned raw-without-manifest objects remain:

- `raw/dukascopy/v1/GBPUSD/2020/05/01/BID_candles_min_1.bi5`;
- `raw/dukascopy/v1/USDJPY/2015/08/03/ASK_candles_min_1.bi5`;
- `raw/dukascopy/v1/USDJPY/2022/11/17/BID_candles_min_1.bi5`.

The supported recovery path is the fresh exact-gap cycle. A missing manifest puts the exact key into the sparse plan. Reacquisition validates source bytes locally, then cloud mirroring verifies/writes the raw object before attempting the manifest object.

This ordering is now covered by an explicit regression test: if the immutable cloud raw rejects the refetched bytes, `CloudMirrorError` propagates immediately and the manifest PUT is never attempted. Therefore recovery cannot create a manifest that blesses bytes different from the already-stored immutable raw, and raw deletion/overwrite is never used to force accounting to pass.

The final acceptance runbook now documents this fail-closed raw-only reconciliation contract.

Verification evidence:

- PR-head test run `34368149054` passed workflow YAML validation, unit tests, and compile;
- golden/network source jobs skipped under `[phase1-no-source]`;
- no Dukascopy acquisition or Supabase deployment was introduced by this change.

## Raw-only 404 cross-object ingest guard — MERGED / VERIFIED / UNDEPLOYED

PR #31 `[phase1-no-source] Phase 1: reject not_found manifests beside existing raw` merged to `main` at:

- `e15de09f70939453db0c59a01bd4c94a7b684d28`

A raw-only exact-gap key can be dangerous if a later source retry returns HTTP 404: without a cross-object guard, a new `not_found` manifest could be stored beside an already-existing immutable raw object. Final acceptance would detect the inconsistency later, but the immutable manifest would make recovery materially harder.

The repository `fmp-raw-ingest` source now protects this state before upload:

- canonical `not_found` manifests map to their exact raw counterpart path;
- the ingest function checks that raw path with a private Storage download using `cache: no-store`;
- if raw exists, the manifest is rejected with HTTP 409 `raw_present_for_not_found_manifest`;
- only verified missing-key/not-found Storage errors are treated as absence;
- any other Storage lookup error fails closed;
- complete manifests and normal raw uploads retain the existing immutable/idempotent behavior.

DEC-012, the final acceptance runbook, and the ingest README now record this rule.

Verification evidence:

- RED Edge run `34368654147` failed exactly because the new helper exports were absent;
- GREEN implementation Edge run `34368795330` passed Deno tests and entrypoint type-check;
- GREEN final Edge run `34368975336` passed;
- Python/test workflow `34368975076` passed;
- golden/network source jobs skipped under `[phase1-no-source]`;
- **the Edge Function was not deployed while repair sweep 2 is active**.

Operational requirement after sweep 2 stops: deploy the tested repository version of `fmp-raw-ingest` before any fresh exact-gap pass that may include the known raw-only keys. This is separate from `fmp-raw-audit`, which remains undeployed until the final structural/provenance stage.

## Complete-manifest cloud-raw invariant — MERGED / VERIFIED / UNDEPLOYED

PR #32 `[phase1-no-source] Phase 1: require complete manifests to match cloud raw` merged to `main` at:

- `40795bff53058f8314ef374b0f97b0cb3a9d30fb`

The repository ingest source now enforces both sides of the manifest/raw cross-object invariant before immutable manifest storage:

- malformed manifest JSON is rejected with HTTP 400;
- unknown manifest statuses are rejected with HTTP 400;
- a `not_found` manifest is accepted only when the matching raw object is verified absent;
- a `complete` manifest is accepted only when the matching raw object already exists;
- the server downloads that raw object with `cache: no-store` and requires exact SHA-256 and byte-size agreement with the manifest;
- a missing raw counterpart or raw/manifest mismatch returns HTTP 409;
- Storage lookup failures other than a verified missing-key result fail closed.

This turns the client-side raw-before-manifest ordering into a server-enforced invariant and prevents a malformed or inconsistent manifest from becoming an immutable cloud object.

Verification evidence:

- RED Edge run `34370385038` failed exactly because `manifestStorageInvariant` did not yet exist;
- GREEN implementation Python run `34370544210` passed;
- GREEN implementation Edge run `34370544201` passed Deno tests and entrypoint type-check;
- final PR-head Python run `34370646499` passed;
- final PR-head Edge run `34370646479` passed;
- golden/source jobs skipped under `[phase1-no-source]`;
- **the Edge Function was not deployed while repair sweep 2 is active**.

Operational requirement after sweep 2 stops: deploy the tested repository `fmp-raw-ingest` version containing PR #31 and PR #32 before any fresh exact-gap pass. The separate read-only `fmp-raw-audit` remains undeployed until the later final provenance stage.

## Canonical manifest ingest schema — MERGED / VERIFIED / UNDEPLOYED

PR #33 `[phase1-no-source] Phase 1: validate canonical manifest schema at ingest` merged to `main` at:

- `1864e52768a7d0d35fee523fb7b46649de46e2fe`

Before immutable manifest storage, the repository `fmp-raw-ingest` source now requires the exact frozen Phase 1 manifest schema and path/body identity:

- the field set must be exact; extra or missing fields are rejected;
- path-derived pair, side, UTC date, source URL, retrieval method, 1m granularity, BI5 source format, 24-byte record size, and zero-based source-month semantics must match the manifest body;
- `retrieved_at_utc` must be timezone-aware;
- `complete` manifests require HTTP 2xx, lowercase SHA-256, positive compressed size, and 1..1440 records;
- `not_found` manifests require HTTP 404 with null SHA/size/records;
- malformed JSON, invalid identity, invalid timestamps, unknown statuses, and inconsistent status metadata fail before immutable storage;
- PR #31/#32 cross-object raw absence/presence/hash/size checks then run only on a canonical manifest body.

Verification evidence:

- RED Edge run `34370969633` failed because `validateManifestForStorage` did not yet exist;
- the first implementation's Deno tests all passed, but Edge run `34371146760` correctly failed entrypoint type-check because the new validator import was missing;
- the import was fixed at `d6b5ae56743212cde86d7565b097dfee54022217`;
- GREEN implementation Edge run `34371245289` and Python run `34371245177` passed;
- final PR-head Edge run `34371361406` and Python run `34371361403` passed;
- golden/source jobs skipped under `[phase1-no-source]`;
- **the Edge Function was not deployed while repair sweep 2 is active**.

Operational requirement after sweep 2 stops: deploy the tested repository `fmp-raw-ingest` version containing PR #31, PR #32, and PR #33 before any fresh exact-gap source pass. The separate read-only `fmp-raw-audit` remains undeployed until the later final provenance stage.

## Frozen ingest object-date namespace — MERGED / VERIFIED / UNDEPLOYED

PR #34 `[phase1-no-source] Phase 1: restrict ingest paths to frozen valid dates` merged to `main` at:

- `08b53ba7b05c18c80b569c5033ac84f83a4b9dfa`

The repository `fmp-raw-ingest` path gate previously enforced only canonical-looking regex structure. A trusted-workflow bug could therefore submit an impossible calendar date or a date outside the frozen Phase 1 snapshot and create an unexpected immutable raw/manifest object.

The ingest source now requires every canonical raw/manifest path to resolve to:

- a real Gregorian date;
- on or after `2015-01-01`;
- before `2026-08-21` (therefore through `2026-08-20` inclusive);
- while retaining the existing V1 pair, BID/ASK, zero-based source-month, and canonical filename restrictions.

Verification evidence:

- RED Edge run `34371729935` failed exactly because regex-only validation accepted out-of-range and impossible dates;
- GREEN implementation Edge run `34371837136` and Python run `34371837190` passed;
- final PR-head Edge run `34371960570` and Python run `34371960666` passed;
- golden/source jobs skipped under `[phase1-no-source]`;
- **the Edge Function was not deployed while repair sweep 2 is active**.

Operational requirement after sweep 2 stops: deploy the tested repository `fmp-raw-ingest` version containing PR #31 through PR #34 before any fresh exact-gap source pass.

## Cloud `not_found` promotion policy — MERGED / VERIFIED

PR #35 `[phase1-no-source] Phase 1: block cloud promotion of not_found manifests` merged to `main` at:

- `8a682d204b04dfa22b9f9a9b5c8fb11690e46e92`

DEC-013 now resolves the tension between explicit source rechecks and first-write cloud-manifest immutability.

V1 policy:

- `--recheck-not-found` remains available for local acquisition/revalidation;
- combining `--recheck-not-found` with `--mirror-url` fails before GitHub OIDC setup and before any source request;
- a canonical cloud `not_found` manifest is not promoted in place to `complete`;
- this prevents the unsafe sequence where a later HTTP 200 stores raw first, then the immutable earlier `not_found` manifest rejects the substantive replacement and leaves raw + stale provenance;
- any future cloud 404→200 transition requires an explicitly approved versioned-provenance design rather than mutation/deletion of canonical objects.

No production acquisition workflow currently uses `--recheck-not-found`, so this guard does not alter repair sweep 2.

Verification evidence:

- RED run `34372389889` showed the incompatible flag combination proceeded into mirroring instead of failing before source/OIDC;
- GREEN implementation run `34372492046` passed;
- final PR-head run `34372638407` passed;
- golden/network source jobs skipped under `[phase1-no-source]`;
- no source acquisition or Supabase deployment was introduced by this change.

## Audit Edge platform-JWT configuration — MERGED / VERIFIED / UNDEPLOYED

PR #36 `[phase1-no-source] Phase 1: pin audit Edge JWT configuration` merged to `main` at:

- `397f34a87e14fe495175e8032cf4cccc9fc4f882`

Both Phase 1 Supabase Edge Functions authenticate GitHub Actions with function-level OIDC verification rather than Supabase Auth user JWTs. Supabase's platform `verify_jwt` check runs before function code and defaults to enabled, so the read-only final-provenance function would have rejected GitHub OIDC at the gateway if deployed without an explicit override.

`supabase/config.toml` now pins:

- `functions.fmp-raw-ingest.verify_jwt = false`;
- `functions.fmp-raw-audit.verify_jwt = false`.

A Python regression test requires both settings. The final acceptance runbook now also requires reading back deployed `fmp-raw-audit` metadata and confirming `verify_jwt = false` before dispatching final provenance.

Verification evidence:

- RED run `34376649181` failed exactly because `fmp-raw-audit` was absent from `supabase/config.toml`;
- GREEN run `34376746736` passed after the audit config was pinned;
- golden/network source jobs skipped under `[phase1-no-source]`;
- no Edge Function was deployed and no Dukascopy acquisition was introduced by this change.

Live Supabase deployment remains `fmp-raw-ingest` **version 3**, `verify_jwt = false`, with deployment fingerprint `6650ad4c469231ef2f0de990fead495cd4a8662ce50f1f9135829b7cff61b6fa`. Its retrieved source is still the older pre-PR31 implementation, so the tested repository ingest source must still be deployed after repair sweep 2 becomes idle and before exact-gap source repair begins.

## Exact-gap GitHub timestamp precision guard — MERGED / VERIFIED

PR #37 `[phase1-no-source] Phase 1: close exact-gap timestamp precision race` merged to `main` at:

- `f5bb0db03585577972be740d4f7f899622a27626`

The exact-gap audit timestamp is millisecond-resolution, while GitHub Actions workflow-run `updated_at` timestamps are observable only at whole-second precision. The prior intervening-run guard compared those timestamps directly, so a source-capable run that changed later in the same UTC second as the audit could be reported as the start of that second and appear older than the audit.

The guard now fails closed at GitHub's observable precision boundary:

- the audit timestamp is floored to its UTC second for workflow-history comparison;
- any source-capable acquisition run reported at or after that second invalidates the sparse plan;
- a run from the prior second remains valid;
- same-second ambiguity is resolved by generating a fresh audit rather than guessing event order.

DEC-012 and the Phase 1 acquisition trigger runbook now record this rule.

Verification evidence:

- RED run `34377000840` failed only because a same-second source run was not rejected; the prior-second control passed;
- GREEN implementation run `34377083894` passed;
- final PR-head run `34377171889` passed;
- golden/network source jobs skipped under `[phase1-no-source]`;
- no Dukascopy acquisition or Supabase deployment was introduced by this change.

## Hardened ingest protocol preflight — MERGED / VERIFIED / UNDEPLOYED

PR #38 `[phase1-no-source] Phase 1: require ingest protocol preflight before source` merged to `main` at:

- `65a4bfa26ced78a2b19ac8576f2572f2641d1662`

The post-sweep ingest deployment prerequisite is now machine-enforced rather than relying only on operator discipline.

The hardened repository contract is:

- `fmp-raw-ingest` exports protocol `fmp-raw-ingest-v2`;
- an authenticated GitHub Actions `GET` to the ingest endpoint returns exactly `{"status":"ready","protocol":"fmp-raw-ingest-v2"}`;
- the Python `SupabaseRawMirror` client performs this preflight before any cloud-mirrored source acquisition;
- a malformed response, non-2xx response, unexpected fields, or wrong protocol raises `CloudMirrorError`;
- the CLI invokes preflight immediately after mirror construction and before the first `acquire_chunk` call;
- therefore the currently deployed pre-hardening v3 endpoint (which returns HTTP 405 for GET) causes future current-`main` source runs to fail before Dukascopy access until the tested ingest is deployed.

This does not affect repair sweep 2 because that long-running workflow is pinned to its historical trigger commit and does not execute current-`main` client code.

Verification evidence:

- RED Python run `34377511304` failed only because `SupabaseRawMirror.preflight` did not exist;
- RED Edge run `34377511305` failed only because `INGEST_PROTOCOL` did not exist;
- GREEN implementation Python run `34377686725` passed;
- GREEN implementation Edge run `34377686712` passed Deno tests and entrypoint type-check;
- final PR-head Python run `34377893039` passed;
- final PR-head Edge run `34377892951` passed;
- golden/network source jobs skipped;
- no Supabase deployment or Dukascopy acquisition was introduced by this change.

Operational consequence: after sweep 2 stops, deploy the tested repository `fmp-raw-ingest` first. The next current-`main` cloud-mirrored acquisition cannot proceed until that deployment advertises the exact hardened protocol.

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
2. When sweep 2 stops, confirm no source-capable `phase1-full-acquisition` run is requested/queued/waiting/pending/in-progress.
3. Deploy the tested repository version of `fmp-raw-ingest` containing PR #31 through PR #34; verify the deployed source/version matches `main`. Do not trigger a source smoke merely to deploy it.
4. Run the committed exhaustive cloud audit against the exact **25,500-manifest** frozen plan.
5. If missing manifests remain, materialize a **fresh** `docs/phase1-exact-gap-queue.json` directly from `docs/phase1-exact-gap-audit.sql`.
6. Trigger one `[phase1-exact-gap-batch]` sparse pass. Do **not** rerun the same workflow attempt after partial success/failure.
7. After every sparse pass, generate a fresh cloud audit and fresh exact-gap plan from only still-missing chunks.
8. Continue bounded exact-gap audit/repair cycles until missing manifests reach zero.
9. Reconcile any remaining raw-only objects through immutable/idempotent repair semantics; never delete cloud raw data to make counts match.
10. Run `docs/phase1-final-acceptance-audit.sql` plus the required provenance/recovery-accounting checks.
11. Only after acquisition is idle **and** structural/accounting evidence is complete, deploy the separate read-only `fmp-raw-audit` and run the final cloud provenance workflow.
12. Record Phase 1 PASS/checkpoint only after **25,500 / 25,500** and all integrity gates are proven.
13. Keep Phase 2 locked until that PASS is recorded.

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
