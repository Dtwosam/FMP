# Phase 2 Full-History Materialization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify a source-free, authenticated, exhaustive Phase 2 materialization path for the frozen 2015-01-01 through 2026-08-20 EURUSD/GBPUSD/USDJPY snapshot.

**Architecture:** Extend `fmp-raw-read` trust by one exact workflow ref, then materialize each pair month-by-month through `CloudRawChunkReader`, with four-worker day concurrency, deterministic monthly 1m/5m/15m/1h outputs, full-pair quality analysis, a verified raw ledger, processed manifest, and summary. A manual three-pair GitHub Actions matrix runs the exhaustive job and uploads pair-scoped evidence/artifacts without contacting the historical source or mutating raw storage.

**Tech Stack:** Python 3.12, Polars 1.44.2, `unittest`, Supabase Edge Functions/Deno/TypeScript, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-13-phase2-full-history-design.md`

## Global Constraints

- Frozen pairs: `EURUSD`, `GBPUSD`, `USDJPY`.
- Frozen range: `2015-01-01` inclusive through `2026-08-20` inclusive.
- Expected days per pair: 4,250; expected raw reads per pair: 8,500.
- Raw reads only through protocol `fmp-raw-read-v1` and audience `fmp-supabase-raw-read`.
- `fmp-raw` remains immutable/read-only.
- No Dukascopy/source acquisition, Phase 1 repair, or gap-queue mutation.
- `phase2-full-history.yml` is `workflow_dispatch` only, `main` only by OIDC claim, GitHub-hosted only, with `contents: read` and `id-token: write`.
- Edge trust accepts exactly the golden and full-history workflow refs; no wildcard matching.
- Full-history worker count is bounded to `1..8`; workflow value is exactly `4`.
- No Phase 3 work and no Phase 2 PASS declaration from implementation alone.
- Every commit includes `[phase1-no-source]`.

---

### Task 1: Expand Edge OIDC trust by one exact workflow ref

**Files:**
- Modify: `supabase/functions/fmp-raw-read/validation.ts`
- Modify: `supabase/functions/fmp-raw-read/validation_test.ts`

**Interfaces:**
- Consumes: `assertTrustedGithubReadClaims(claims: Record<string, unknown>): true`
- Produces: the same interface, accepting exactly two workflow refs while preserving every other exact claim.

- [ ] **Step 1: Write failing validation tests**

Add tests equivalent to:

```ts
Deno.test("full-history workflow identity is trusted", () => {
  assertEquals(assertTrustedGithubReadClaims({
    ...trustedClaims,
    workflow_ref: "Dtwosam/FMP/.github/workflows/phase2-full-history.yml@refs/heads/main",
  }), true);
});

Deno.test("unlisted raw-read workflow identity is rejected", () => {
  assertThrows(() => assertTrustedGithubReadClaims({
    ...trustedClaims,
    workflow_ref: "Dtwosam/FMP/.github/workflows/other.yml@refs/heads/main",
  }));
});
```

Keep the existing golden workflow test green.

- [ ] **Step 2: Run Edge tests and observe RED**

Run in CI: `deno test supabase/functions/fmp-raw-read/validation_test.ts`.
Expected: the full-history identity test fails because the current validator pins only the golden workflow.

- [ ] **Step 3: Implement exact two-ref trust**

Keep repository/ref/event/runner claims in `EXPECTED`; move workflow identity to a set:

```ts
const TRUSTED_WORKFLOW_REFS = new Set([
  "Dtwosam/FMP/.github/workflows/phase2-cloud-golden.yml@refs/heads/main",
  "Dtwosam/FMP/.github/workflows/phase2-full-history.yml@refs/heads/main",
]);
```

After validating `EXPECTED`, require `claims.workflow_ref` to be a string member of this set.

- [ ] **Step 4: Run Deno tests/check**

Run all existing Edge tests plus `deno check supabase/functions/fmp-raw-read/index.ts`.
Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `feat: trust full-history cloud reader workflow [phase1-no-source]`.

---

### Task 2: Add deterministic full-history planning and raw ledger

**Files:**
- Create: `src/fmp/data/phase2/full_history.py`
- Create: `tests/test_phase2_full_history.py`

**Interfaces:**
- Produces constants `FULL_HISTORY_START`, `FULL_HISTORY_END_EXCLUSIVE`, `FULL_HISTORY_PAIRS`, `DEFAULT_WORKERS`, `MAX_WORKERS`.
- Produces `_iter_month_ranges(start, end_exclusive)` yielding `(month_start, month_end_exclusive)`.
- Produces `RecordingCompleteRawChunkReader` with `.read(key)` and `.write_ledger(path)`.
- Produces `validate_full_history_ledger(records, pair, start, end_exclusive)`.

- [ ] **Step 1: Write failing planner/ledger tests**

Tests must assert:

```python
self.assertEqual((FULL_HISTORY_END_EXCLUSIVE - FULL_HISTORY_START).days, 4250)
self.assertEqual(len(list(_iter_month_ranges(FULL_HISTORY_START, FULL_HISTORY_END_EXCLUSIVE))), 140)
```

Create complete synthetic ledger rows for a short range and assert missing, duplicate, wrong-pair, wrong-side, wrong-date, and `not_found` rows raise `ValueError`.

- [ ] **Step 2: Run the new Python test and observe RED**

Run: `python -m unittest tests.test_phase2_full_history -v`.
Expected: import/module failures.

- [ ] **Step 3: Implement constants, month iterator, worker validation, and ledger**

Use fixed constants:

```python
FULL_HISTORY_START = date(2015, 1, 1)
FULL_HISTORY_END_EXCLUSIVE = date(2026, 8, 21)
FULL_HISTORY_PAIRS = ("EURUSD", "GBPUSD", "USDJPY")
DEFAULT_WORKERS = 4
MAX_WORKERS = 8
```

`RecordingCompleteRawChunkReader.read()` delegates to a verified reader, raises if body is `None`, and records pair/side/date/SHA/size/status under a lock so it is safe under the executor.

`validate_full_history_ledger` compares the observed identity set and total length against the exact Cartesian product of each date and `(BID, ASK)`.

- [ ] **Step 4: Run test GREEN**

Run the new test module and `python -m compileall -q src tests`.
Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `feat: add frozen Phase 2 full-history plan [phase1-no-source]`.

---

### Task 3: Add month-bounded pair materialization

**Files:**
- Modify: `src/fmp/data/phase2/full_history.py`
- Modify: `tests/test_phase2_full_history.py`
- Reuse: `src/fmp/data/phase2/artifacts.py`, `normalize.py`, `quality.py`, `resample.py`

**Interfaces:**
- Produces `materialize_pair(reader, output_root, pair, *, start, end_exclusive, code_commit, workers) -> dict[str, object]`.
- Produces production wrapper `run_full_history_pair(endpoint, output_root, pair, *, code_commit, workers=4) -> dict[str, object]`.

- [ ] **Step 1: Write failing test-scale materialization test**

Use a short range crossing a month boundary and monkeypatch `normalize_day` with deterministic canonical frames. Assert that materialization creates monthly paths for all four timeframes, pair quality JSON, raw ledger, processed manifest, and summary. Assert every summary digest matches the file on disk and the artifact map contains each expected monthly partition exactly once.

- [ ] **Step 2: Run the new tests and observe RED**

Expected: missing `materialize_pair`/outputs.

- [ ] **Step 3: Implement month processing**

For each month range:

```python
with ThreadPoolExecutor(max_workers=workers) as executor:
    frames = list(executor.map(lambda day: normalize_day(recording_reader, pair, day), days))
month = pl.concat([f for f in frames if not f.is_empty()], how="vertical").sort(["symbol", "timestamp_utc"])
```

Write 1m and each derived timeframe directly to the existing monthly layout with `write_parquet_partition`. Maintain artifact records and total row counts without retaining prior month frames.

After all months, load the ordered 1m partitions, concatenate/sort, and call existing `analyze_quality` once for the pair. Write quality JSON, validate/write the raw ledger, build/write the processed manifest, then write `summary.json` with pair/range/month/read/row/digest/finding-count evidence.

- [ ] **Step 4: Verify deterministic test output**

Run the new tests twice against clean temporary roots and compare non-time-varying evidence fields and partition hashes.

- [ ] **Step 5: Commit**

Commit message: `feat: materialize full Phase 2 pair history [phase1-no-source]`.

---

### Task 4: Add fixed full-history CLI

**Files:**
- Modify: `src/fmp/data/phase2/full_history.py`
- Modify: `tests/test_phase2_full_history.py`

**Interfaces:**
- CLI: `python -m fmp.data.phase2.full_history --endpoint <HTTPS> --pair <PAIR> --out <ROOT> --code-commit <SHA> --workers 4`.

- [ ] **Step 1: Write parser/guard tests**

Assert only the three frozen pairs are accepted, `--workers` rejects 0 and 9, and no `--start`/`--end` arguments exist.

- [ ] **Step 2: Observe RED**

Run the new test module.

- [ ] **Step 3: Implement parser/main**

The CLI must always call `run_full_history_pair` with the frozen date constants. It must never accept an arbitrary date range.

- [ ] **Step 4: Run tests GREEN**

Run the new tests and compileall.

- [ ] **Step 5: Commit**

Commit message: `feat: add fixed Phase 2 full-history CLI [phase1-no-source]`.

---

### Task 5: Add source-free full-history Actions workflow

**Files:**
- Create: `.github/workflows/phase2-full-history.yml`
- Create: `tests/test_phase2_full_history_workflow.py`

**Interfaces:**
- Manual workflow with fixed three-pair matrix and exact `fmp-raw-read` endpoint.

- [ ] **Step 1: Write failing workflow guard test**

Assert the workflow text contains `workflow_dispatch`, `contents: read`, `id-token: write`, all three pairs, `python -m fmp.data.phase2.full_history`, `--workers 4`, the exact endpoint, `actions/checkout@v6`, `actions/setup-python@v6`, `actions/upload-artifact@v6`, `include-hidden-files: true`, and `if-no-files-found: error`.

Assert it does not contain `push:`, `pull_request:`, `schedule:`, `datafeed.dukascopy.com`, `fmp.data.cli fetch`, `fetch-plan`, `acquire_chunk`, `repair`, `upload(`, or arbitrary `start`/`end` inputs.

- [ ] **Step 2: Observe RED**

Run `python -m unittest tests.test_phase2_full_history_workflow -v`.

- [ ] **Step 3: Implement workflow**

Use a fixed matrix and 330-minute job timeout. Run the CLI into `.phase2-full-history/${{ matrix.pair }}`. Add a Python verification step that checks pair/range, `month_count == 140`, `raw_read_count == 8500`, `raw_read_counts == {"ASK": 4250, "BID": 4250}`, all four timeframe row counts positive, manifest/ledger/quality paths exist, and all recorded SHA-256 strings are 64 lowercase hex characters. Upload the complete pair directory as `phase2-full-history-${{ matrix.pair }}`.

- [ ] **Step 4: Validate YAML and tests**

Run `ruby scripts/validate_workflow_yaml.rb .github/workflows` and all workflow guard tests.

- [ ] **Step 5: Commit**

Commit message: `ci: add Phase 2 full-history materialization [phase1-no-source]`.

---

### Task 6: Update project state without claiming PASS

**Files:**
- Modify: `docs/project-state.md`

**Interfaces:**
- Documents the successful bounded cloud proof and identifies exhaustive full-history materialization as the active Phase 2 milestone.

- [ ] **Step 1: Update the Phase 2 state**

Record the successful `phase2-cloud-golden` run `34780748485`, main SHA `c2aa08e36157544d891375ea5aba44915d702d76`, artifact ID `10325445851`, artifact SHA-256 `458f827676be8985cd684549aa68574cbcb772531401dca4e9c7404c9a53d1cc`, exact four verified raw chunks, and successful 1m/quality/5m/15m/1h evidence.

Change the next milestone to exhaustive full-history materialization and Phase 2 acceptance evidence review. Preserve Phase status as active/not PASS.

- [ ] **Step 2: Review wording**

Ensure the file does not claim full-history completion, Phase 2 PASS, or Phase 3 start.

- [ ] **Step 3: Commit**

Commit message: `docs: advance Phase 2 to full-history materialization [phase1-no-source]`.

---

### Task 7: Fresh verification, PR, merge, deploy, and execution gate

**Files:**
- No new implementation files unless verification exposes a defect.

- [ ] **Step 1: Fresh branch verification**

Require green:

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
ruby scripts/validate_workflow_yaml.rb .github/workflows
deno test supabase/functions/fmp-raw-ingest/*_test.ts
deno test supabase/functions/fmp-raw-audit/*_test.ts
deno test supabase/functions/fmp-raw-read/*_test.ts
deno check supabase/functions/fmp-raw-ingest/index.ts
deno check supabase/functions/fmp-raw-audit/index.ts
deno check supabase/functions/fmp-raw-read/index.ts
```

Use repository CI as the executable environment when no connected development machine is available.

- [ ] **Step 2: Full diff review**

Verify only intended files changed, `docs/phase1-exact-gap-queue.json` is absent, no acquisition/source path was introduced, and Edge storage mutation guard remains intact.

- [ ] **Step 3: Open `[phase1-no-source]` PR**

PR title must include `[phase1-no-source]` before source-capable PR workflows evaluate. Require tests/Edge CI green and Phase 1 source-capable workflows skipped.

- [ ] **Step 4: Squash merge latest green head**

Merge only with exact expected head SHA. Squash message must include `[phase1-no-source]`.

- [ ] **Step 5: Post-merge checks**

Verify main CI green and confirm no Phase 1 acquisition run executed for the merge SHA.

- [ ] **Step 6: Deploy only `fmp-raw-read`**

Deploy the merged `index.ts` + `validation.ts` to Supabase project `htjqqzlezyguveuajuat` with `verify_jwt=false` because the function implements custom GitHub OIDC validation. Do not deploy or mutate other functions/buckets. Verify deployed contents/version.

- [ ] **Step 7: Manual full-history dispatch gate**

The connected GitHub tool cannot create a new `workflow_dispatch` event. Stop only at this external platform boundary and ask the user to run `phase2-full-history` on `main`. After dispatch, inspect all three jobs, logs, pair artifacts, processed manifests, ledgers, quality reports, and digests before considering Phase 2 acceptance.
