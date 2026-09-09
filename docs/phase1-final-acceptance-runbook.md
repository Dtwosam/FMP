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
5. Download the `phase1-cloud-provenance-<run_id>` artifact and retain
   `phase1-cloud-provenance.json`.

The verifier checks all 25,500 manifest bodies for exact Phase 1
schema/identity/source semantics and, for every `complete` manifest, checks
the matching cloud raw object's server-side SHA-256 and compressed size.
`not_found` manifests must carry HTTP 404 and null raw metadata.

Required result:

- `planned_chunks = 25500`
- `complete + not_found = 25500`
- `issues = 0`
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
