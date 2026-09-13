# Phase 2 Cloud Raw Read Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fail-closed authenticated Supabase raw reader and prove a tiny source-free real-cloud Phase 2 materialization for EURUSD and USDJPY without mutating Phase 1 data or starting full-history processing.

**Architecture:** A new `fmp-raw-read` Edge Function validates a pinned GitHub OIDC identity, derives canonical Phase 1 storage paths from `{pair, side, date_utc}`, validates the frozen manifest contract, verifies raw SHA/size, and returns exact `.bi5` bytes with immutable identity headers. Python `CloudRawChunkReader` acquires the matching GitHub OIDC token, applies the same bounded retry policy, verifies every response invariant, and feeds the existing Phase 2 pipeline. A manual-only workflow exercises two real cloud chunks and uploads bounded 1m/quality/5m/15m/1h evidence.

**Tech Stack:** Python 3.12, pytest, urllib, Supabase Edge Functions/Deno, TypeScript, `jose@5.10.0`, `@supabase/supabase-js@2.116.0`, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-13-phase2-cloud-read-design.md`

## Global Constraints

- Phase 1 is immutable and remains PASS at `fmp-v1-phase1-source-of-truth`.
- Do not modify `docs/phase1-exact-gap-queue.json`.
- Do not contact Dukascopy from the new workflow or cloud reader proof.
- Do not invoke Phase 1 acquisition or repair.
- Do not upload, update, delete, list, proxy arbitrary paths, or issue signed URLs from `fmp-raw-read`.
- Do not start full-history Phase 2 processing.
- Do not declare Phase 2 PASS.
- Do not start Phase 3.
- Every commit in this slice includes `[phase1-no-source]`.
- `fmp-raw-read` protocol is exactly `fmp-raw-read-v1`.
- GitHub OIDC audience is exactly `fmp-supabase-raw-read`.
- Trusted workflow is exactly `Dtwosam/FMP/.github/workflows/phase2-cloud-golden.yml@refs/heads/main`.
- Allowed pairs: `EURUSD`, `GBPUSD`, `USDJPY`; allowed sides: `BID`, `ASK`; dates: 2015-01-01 through 2026-08-20 inclusive.
- Default retry policy: 3 attempts and injectable 1-second delay; retry only connection/timeouts/OSError/429/5xx.

---

### Task 1: Edge request/auth/path validation

**Files:**
- Create: `supabase/functions/fmp-raw-read/validation.ts`
- Create: `supabase/functions/fmp-raw-read/validation_test.ts`

**Interfaces:**
- Produces: `READ_PROTOCOL`, `assertTrustedGithubReadClaims(claims)`, `validateReadRequest(payload)`, `deriveReadPaths(request)`.
- `validateReadRequest` returns `{ pair: "EURUSD" | "GBPUSD" | "USDJPY"; side: "BID" | "ASK"; date_utc: string }`.
- `deriveReadPaths` returns `{ manifestPath: string; rawPath: string }` using zero-based source month.

- [ ] **Step 1: Write RED Deno tests** for exact claim pinning, exact three-field body, allowed identity values, real-date parsing, frozen date bounds, extra/missing field rejection, and zero-based path derivation.
- [ ] **Step 2: Run** `deno test supabase/functions/fmp-raw-read/validation_test.ts` and verify failure because the module/functions do not exist.
- [ ] **Step 3: Implement minimal validation** with constants for protocol/claims, strict object-key checks, exact string values, `Date.UTC` round-trip calendar validation, and canonical path derivation.
- [ ] **Step 4: Re-run** the Deno test and verify PASS.
- [ ] **Step 5: Commit** `test/feat: add raw read request validation [phase1-no-source]`.

### Task 2: Exact Phase 1 manifest validation

**Files:**
- Modify: `supabase/functions/fmp-raw-read/validation.ts`
- Modify: `supabase/functions/fmp-raw-read/validation_test.ts`

**Interfaces:**
- Produces: `validateManifestForRead(request, manifest)` returning `{ status: "complete"; sha256: string; compressedSizeBytes: number; records: number } | { status: "not_found" }` or throwing on invalid provenance.

- [ ] **Step 1: Add RED tests** for exact manifest field set and types, non-boolean integer `manifest_version = 1`, exact source URL/retrieval/source/granularity/format/record-size/month-indexing/identity, UTC timestamp, complete rules, and verified not-found rules.
- [ ] **Step 2: Run** the Deno validation test and confirm the new cases fail.
- [ ] **Step 3: Implement the validator** so it mirrors `src/fmp/data/manifest.py` exactly, including zero-based Dukascopy URL month and complete/not-found consistency.
- [ ] **Step 4: Re-run** and verify PASS.
- [ ] **Step 5: Commit** `feat: validate Phase 1 manifests in raw reader [phase1-no-source]`.

### Task 3: Read-only Edge Function behavior

**Files:**
- Create: `supabase/functions/fmp-raw-read/index.ts`
- Modify: `supabase/config.toml`
- Modify: `tests/test_edge_dependency_pins.py`
- Modify: `tests/test_edge_function_config.py`

**Interfaces:**
- Authenticated GET returns exactly `{status:"ready", protocol:"fmp-raw-read-v1"}`.
- Authenticated POST accepts only pair/side/date identity.
- Complete response: exact BI5 bytes, `application/octet-stream`, `X-FMP-*` identity/integrity headers, `Cache-Control: no-store`.
- Verified not-found response: HTTP 404 exact JSON identity schema.

- [ ] **Step 1: Add RED Python/config tests** requiring `fmp-raw-read` dependency pins and `verify_jwt = false`.
- [ ] **Step 2: Add RED Deno unit coverage** around response helpers/integrity behavior where separable from Supabase I/O.
- [ ] **Step 3: Run targeted tests** and verify expected failures.
- [ ] **Step 4: Implement `index.ts`** using `jose` OIDC validation, service secret only inside the function, manifest-first `download(..., {cache:"no-store"})`, SHA-256/size recomputation, and no storage mutation methods.
- [ ] **Step 5: Update `supabase/config.toml`** with `[functions.fmp-raw-read] verify_jwt = false`.
- [ ] **Step 6: Re-run targeted Deno/Python tests** and verify PASS.
- [ ] **Step 7: Commit** `feat: add read-only Supabase raw read function [phase1-no-source]`.

### Task 4: Python GitHub OIDC provider and transport

**Files:**
- Modify: `src/fmp/data/phase2/raw_reader.py`
- Create: `tests/test_phase2_cloud_raw_reader.py`

**Interfaces:**
- Produces `GithubRawReadOidcTokenProvider.from_environment()` and `get_token()`.
- Uses audience `fmp-supabase-raw-read`.
- Reuses existing `CloudHttpResponse`/GET transport conventions from `src/fmp/data/cloud.py`.

- [ ] **Step 1: Write RED tests** for missing env credentials, exact audience query parameter, bearer request token, JWT-expiry cache reuse, transient exception/429/5xx retries, and permanent 4xx/malformed token-response no-retry behavior.
- [ ] **Step 2: Run** `pytest tests/test_phase2_cloud_raw_reader.py -q` and confirm failures.
- [ ] **Step 3: Implement minimal provider** with validated retry settings, 3 attempts, 1-second injectable sleep, expiry caching, and no retry on permanent/protocol failures.
- [ ] **Step 4: Re-run** targeted tests and verify PASS.
- [ ] **Step 5: Commit** `feat: add cloud raw read OIDC provider [phase1-no-source]`.

### Task 5: `CloudRawChunkReader`

**Files:**
- Modify: `src/fmp/data/phase2/raw_reader.py`
- Modify: `tests/test_phase2_cloud_raw_reader.py`

**Interfaces:**
- Produces `CloudRawChunkReader(endpoint, token_provider, ..., max_attempts=3, retry_delay_seconds=1.0)` implementing `read(key: RawChunkKey) -> bytes | None`.

- [ ] **Step 1: Add RED tests** for exact POST body, auth/content headers, successful octet-stream response, exact `X-FMP-*` identity/provenance verification, client-side SHA/size recomputation, verified exact not-found JSON -> `None`, malformed success/not-found schemas, wrong protocol/identity/content-type/SHA/size, permanent 4xx no-retry, and transient exceptions/429/5xx retries.
- [ ] **Step 2: Run targeted tests** and verify failures.
- [ ] **Step 3: Implement transport + reader** using HTTPS-only endpoint validation, exact JSON body, strict header/schema validation, and `RawReadError` for every fail-closed condition.
- [ ] **Step 4: Re-run targeted tests** and verify PASS.
- [ ] **Step 5: Run existing Phase 2 raw-reader/normalization tests** to verify protocol compatibility.
- [ ] **Step 6: Commit** `feat: add CloudRawChunkReader [phase1-no-source]`.

### Task 6: Bounded cloud golden proof command/script

**Files:**
- Create or modify a focused Phase 2 script/CLI module under `src/fmp/data/phase2/` or existing CLI entrypoint, following current project conventions.
- Create: `tests/test_phase2_cloud_golden.py` if a dedicated module is added.

**Interfaces:**
- Consumes `CloudRawChunkReader` and the existing decoder/normalize/quality/resample/artifact pipeline.
- Produces an evidence directory containing a machine-readable summary and canonical 1m/quality/5m/15m/1h artifacts for an explicit tiny allowlist only.

- [ ] **Step 1: Inspect current `process-phase2` orchestration and artifact APIs** and select the smallest reusable path without adding full-history iteration.
- [ ] **Step 2: Write RED tests** proving only explicit requested keys are read, both EURUSD and USDJPY are required, no source client is constructed, and summary evidence binds raw identities/digests to generated 1m/quality/5m/15m/1h outputs.
- [ ] **Step 3: Run targeted tests** and confirm failure.
- [ ] **Step 4: Implement the bounded proof path** with no default history range and no fallback to local/source acquisition.
- [ ] **Step 5: Re-run targeted tests** and verify PASS.
- [ ] **Step 6: Commit** `feat: add bounded cloud golden proof [phase1-no-source]`.

### Task 7: Manual source-free GitHub Actions workflow

**Files:**
- Create: `.github/workflows/phase2-cloud-golden.yml`
- Create or modify workflow guard tests under `tests/`.

**Interfaces:**
- Trigger: `workflow_dispatch` only.
- Permissions: `contents: read`, `id-token: write` only.
- Edge endpoint: `https://htjqqzlezyguveuajuat.supabase.co/functions/v1/fmp-raw-read`.
- Artifact upload: bounded evidence directory from Task 6.

- [ ] **Step 1: Write RED workflow tests** asserting manual-only trigger, exact permissions, fixed endpoint, explicit bounded EURUSD + USDJPY keys, no Dukascopy/source/acquire/repair invocation, no full-history loop, and evidence artifact upload.
- [ ] **Step 2: Run workflow tests/YAML parse** and confirm failure because workflow is absent.
- [ ] **Step 3: Create workflow** that checks out, sets up Python/dependencies, runs the bounded cloud golden proof, and uploads its evidence.
- [ ] **Step 4: Re-run workflow tests/YAML validation** and verify PASS.
- [ ] **Step 5: Commit** `ci: add Phase 2 cloud golden proof [phase1-no-source]`.

### Task 8: Fresh branch verification and PR

**Files:** none unless verification finds defects.

- [ ] **Step 1:** Run the complete Python unit suite from a fresh checkout.
- [ ] **Step 2:** Run `python -m compileall src tests`.
- [ ] **Step 3:** Parse/validate all workflow YAML.
- [ ] **Step 4:** Run all Deno/Edge validation tests.
- [ ] **Step 5:** Run git diff/check equivalent and confirm `docs/phase1-exact-gap-queue.json` is untouched.
- [ ] **Step 6:** Open the PR to `main` and inspect PR-level CI.
- [ ] **Step 7:** Confirm Phase 1 source-capable PR workflows/jobs are skipped.
- [ ] **Step 8:** Review the complete PR diff for security, provenance, retry classification, no-storage-write guarantee, bounded workflow scope, and absence of full-history logic.
- [ ] **Step 9:** Fix any defects through additional RED → GREEN commits carrying `[phase1-no-source]`.
- [ ] **Step 10:** Squash merge only when latest CI is green.

### Task 9: Post-merge verification, deploy, and real evidence

**Files:** no repository changes expected.

- [ ] **Step 1:** Verify merged `main` CI is green.
- [ ] **Step 2:** Confirm any push-triggered `phase1-full-acquisition` run is `SKIPPED` and no Phase 1 acquisition executed.
- [ ] **Step 3:** Deploy only Supabase Edge Function `fmp-raw-read` to project `htjqqzlezyguveuajuat`.
- [ ] **Step 4:** Dispatch `.github/workflows/phase2-cloud-golden.yml` on `main`.
- [ ] **Step 5:** Inspect the real workflow jobs and uploaded evidence artifacts; verify both EURUSD and USDJPY chunks were read through the deployed function and canonical 1m + quality + 5m/15m/1h evidence exists.
- [ ] **Step 6:** Record the bounded proof result without declaring Phase 2 PASS and without starting full-history processing.
