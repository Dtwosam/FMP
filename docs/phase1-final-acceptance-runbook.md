# Phase 1 Final Acceptance Runbook

This runbook is the only supported path for declaring the frozen Dukascopy V1
historical snapshot complete.

## Scope

Frozen Phase 1 snapshot:

- pairs: EURUSD, GBPUSD, USDJPY
- sides: BID, ASK
- start: 2015-01-01
- end exclusive: 2026-08-21
- planned manifests: 25,500
- canonical plan SHA-256: `2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6`

A Phase 1 PASS proves acquisition completeness and cloud provenance. It does
not prove quote cleanliness, gap acceptability, session correctness, or derived
bar correctness; those remain Phase 2.

## Preconditions

1. No `phase1-full-acquisition` workflow run may be requested, queued, waiting,
   pending, or in progress.
2. Evidence A and B must be generated after the latest completed `phase1-full-acquisition` workflow run that will be used as the final provenance baseline.
3. Exact-gap repair must have reduced the frozen plan to:
   - 25,500 present manifests;
   - zero missing manifests;
   - zero raw-without-manifest objects;
   - zero unexpected raw or manifest paths.
4. Do not delete immutable cloud objects to satisfy accounting.
5. The read-only `fmp-raw-audit` Edge Function must not be deployed until
   acquisition is idle and the structural snapshot is complete.

## Raw-only reconciliation before final evidence

If the structural audit shows planned raw objects without matching manifests, do not delete or overwrite those raw objects.

The supported recovery path is the fresh exact-gap repair cycle:

1. The missing manifest causes that exact pair/date/side key to appear in the fresh exact-gap plan.
2. The runner reacquires the source chunk and validates it locally.
3. Cloud mirroring writes/verifies the raw object **before** attempting the manifest object.
4. If the refetched raw bytes match the immutable cloud raw, the ingest layer returns success/already-verified and the canonical manifest can then be mirrored.
5. If the refetched raw bytes differ, the immutable raw PUT fails and manifest upload is never attempted. Stop and investigate; never create a manifest that blesses different bytes and never delete the original raw to force accounting to pass.
6. If the source now returns HTTP 404 for a key whose immutable raw already exists, the repository ingest source rejects the `not_found` manifest with HTTP 409.
7. For every `complete` manifest, the repository ingest source requires the matching raw object to already exist and verifies its server-side SHA-256 and byte size against the manifest before storing the manifest.
8. Before cross-object checks, every manifest body must exactly match the frozen Phase 1 schema and its path-derived pair/side/date/source identity; extra or missing fields, malformed JSON, invalid timestamps, unknown statuses, or inconsistent status metadata fail closed.
9. Raw/manifest metadata mismatches and Storage lookup failures other than a verified missing-key result also fail closed.
10. Both raw and manifest object paths must resolve to a real calendar date inside the frozen 2015-01-01 through 2026-08-20 interval; impossible or out-of-snapshot paths are rejected before immutable storage.

Before executing a fresh exact-gap pass that may include raw-only keys, deploy the tested repository version of `fmp-raw-ingest` containing these cross-object guards. Do not deploy it while a Phase 1 acquisition run is active. Read back the deployed metadata and source, require `verify_jwt = false`, and confirm that authenticated GET returns exactly `{"status":"ready","protocol":"fmp-raw-ingest-v2"}`. The current main-branch mirror client also enforces this preflight before its first source request.

This ordering is a Phase 1 safety property. Final Evidence A/B must still show `raw_without_manifest = 0` before provenance verification begins.

## Evidence A — Structural cloud ledger

Run:

- `docs/phase1-final-acceptance-audit.sql`

Save the single result object as `phase1-structural.json`.

Required result:

- `report_version = 1`
- `scope = phase1_structural_acceptance`
- `frozen_start_date = 2015-01-01`
- `frozen_end_date_exclusive = 2026-08-21`
- `expected_manifests = 25500`
- `present_manifests = 25500`
- `missing_manifests = 0`
- `unexpected_manifest_paths = 0`
- `raw_without_manifest = 0`
- `unexpected_raw_paths = 0`
- `structural_gate_pass = true`

If any field fails, stop and repair. Do not run the final provenance workflow.

## Evidence B — Recovery/accounting ledger

Run:

- `docs/phase1-recovery-accounting-audit.sql`

Save the returned `phase1_recovery_accounting` object (or its one-key wrapper)
as `phase1-accounting.json`.

Required result:

- frozen plan identity matches this runbook;
- expected/present manifests are both 25,500;
- missing manifests are zero;
- raw-without-manifest and unexpected path counts are zero;
- raw-backed + manifest-only inferred not_found = 25,500;
- `pair_side_breakdown` contains exactly six unique rows: EURUSD/GBPUSD/USDJPY × BID/ASK;
- each pair/side row has `expected_manifests = present_manifests = 4250`, zero missing/raw-without-manifest, and raw-backed + inferred not_found = 4,250;
- the six row-level raw-backed/not_found counts reconcile exactly to the accounting totals;
- `accounting_gate_pass = true`.

This is accounting evidence only. It does not replace manifest-body/raw
provenance verification.

## Evidence C — Full cloud provenance

Only after Evidence A and B pass and acquisition is idle:

1. Deploy the repository version of the separate read-only Supabase Edge
   Function `fmp-raw-audit` with its committed `verify_jwt = false` setting.
   This function validates GitHub OIDC inside its own code; Supabase's platform
   JWT gate must therefore remain disabled for this endpoint.
2. Read back the deployed function metadata and require `verify_jwt = false`
   before running provenance. If the deployed setting differs, stop.
3. Do not modify or redeploy `fmp-raw-ingest` as part of this step.
4. Manually dispatch:
   - `.github/workflows/phase1-final-cloud-audit.yml`
5. The workflow itself refuses to run while Phase 1 acquisition is active.
6. It pages the full `phase1-full-acquisition` history and selects the most recently **updated source-capable** run as the baseline. Push-triggered `[phase1-no-source]` runs are ignored because their acquisition jobs are suppressed; manual `workflow_dispatch` runs remain source-capable regardless of head-commit text. The selected baseline must have `status = completed`.
7. It records an audit-guard UTC timestamp before that initial source-capable idle/baseline check, then re-scans the complete acquisition workflow history after provenance verification. Any source-capable run updated at or after that observable UTC second invalidates the evidence, including reruns that reuse older workflow run IDs.
8. It repeats the source-capable baseline selection after provenance and requires the same baseline run ID **and** completion/activity timestamp. This catches pre-audit reruns through baseline selection and in-audit reruns through the guard, while unrelated no-source pushes do not invalidate evidence.
9. Only after both stability checks pass does the workflow stamp the provenance JSON with the acquisition baseline ID, the baseline completion timestamp, and `acquisition_unchanged_during_verification = true`.
10. Download the `phase1-cloud-provenance-<run_id>` artifact and retain both
    `phase1-cloud-provenance.json` and `.phase1-final-acquisition-run-guard.json`.

The verifier checks all 25,500 manifest bodies for exact Phase 1
schema/identity/source semantics and, for every `complete` manifest, checks
the matching cloud raw object's server-side SHA-256 and compressed size.
`not_found` manifests must carry HTTP 404 and null raw metadata.

Required result:

- `plan_sha256 = 2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6`
- `planned_chunks = 25500`
- `complete + not_found = 25500`
- `issues = 0`
- `acquisition_baseline_run_id` is a positive integer
- `acquisition_baseline_completed_at_utc` is a UTC-zero timestamp
- `acquisition_history_guard_version = 1`
- `acquisition_history_guard_started_at_utc` is a UTC-zero timestamp at or after the acquisition baseline completion time
- both Evidence A and Evidence B `audited_at_utc` timestamps are at or after that acquisition baseline completion time
- `acquisition_unchanged_during_verification = true`
- `ready = true`

## Evidence D — Cross-report acceptance

Run:

```bash
python -m fmp.data.cli accept-phase1 \
  --structural-json phase1-structural.json \
  --accounting-json phase1-accounting.json \
  --provenance-json phase1-cloud-provenance.json \
  > phase1-final-acceptance.json
```

The command exits zero only when every independent gate passes and the reports
agree with one another.

Important cross-checks include:

- structural and accounting frozen snapshot identities match this runbook;
- accounting contains one complete, unique, totals-reconciled row for every frozen pair/side;
- provenance plan SHA-256 matches the frozen plan fingerprint above;
- provenance carries a valid source-capable acquisition baseline run ID/completion time, binds final acquisition-history guard version 1 and its UTC start timestamp into the same JSON, keeps those times non-future, and confirms acquisition remained unchanged during verification;
- structural and accounting `audited_at_utc` timestamps use UTC-zero offsets, are not older than the acquisition baseline completion time, and are not future-dated relative to acceptance execution;
- structural present = accounting present = provenance planned = 25,500;
- structural raw objects = accounting raw-backed = provenance complete;
- accounting inferred not_found = provenance not_found.

Required final result:

- `checks_failed = 0`
- `ready = true`

## Recording PASS

Only after Evidence A-D all pass:

1. Review the final evidence and the latest CI state using the project's
   verification-before-completion rule.
2. Record exact audit timestamps, report/artifact identifiers, counts, and
   relevant commits in `docs/project-state.md`.
3. Record Phase 1 status as PASS.
4. Create the Phase 1 checkpoint/ref.
5. Only then unlock Phase 2 — Validation, Normalization & Derived Bars.

Any mismatch or unexplained object state keeps Phase 1 open.
