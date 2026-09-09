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

1. No `phase1-full-acquisition` workflow run may be queued, waiting, pending,
   or in progress.
2. Exact-gap repair must have reduced the frozen plan to:
   - 25,500 present manifests;
   - zero missing manifests;
   - zero raw-without-manifest objects;
   - zero unexpected raw or manifest paths.
3. Do not delete immutable cloud objects to satisfy accounting.
4. The read-only `fmp-raw-audit` Edge Function must not be deployed until
   acquisition is idle and the structural snapshot is complete.

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
   Function `fmp-raw-audit`.
2. Do not modify or redeploy `fmp-raw-ingest` as part of this step.
3. Manually dispatch:
   - `.github/workflows/phase1-final-cloud-audit.yml`
4. The workflow itself refuses to run while Phase 1 acquisition is active.
5. It snapshots the latest `phase1-full-acquisition` run ID before provenance verification and fails if that run ID changes before verification completes, so an acquisition that starts and finishes during the audit still invalidates the evidence.
6. Only after that stability check passes does the workflow stamp the provenance JSON with the acquisition baseline ID and `acquisition_unchanged_during_verification = true`.
7. Download the `phase1-cloud-provenance-<run_id>` artifact and retain
   `phase1-cloud-provenance.json`.

The verifier checks all 25,500 manifest bodies for exact Phase 1
schema/identity/source semantics and, for every `complete` manifest, checks
the matching cloud raw object's server-side SHA-256 and compressed size.
`not_found` manifests must carry HTTP 404 and null raw metadata.

Required result:

- `plan_sha256 = 2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6`
- `planned_chunks = 25500`
- `complete + not_found = 25500`
- `issues = 0`
- `acquisition_baseline_run_id` is a non-negative integer
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
- provenance carries a valid acquisition baseline run ID and confirms acquisition remained unchanged during verification;
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
