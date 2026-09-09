# Phase 1 Full Acquisition Trigger

This file exists only as a controlled GitHub Actions trigger surface for Phase 1 raw-data persistence.

- Ordinary edits/creation without `[phase1-full]` in the commit message run the bounded cloud smoke only.
- A commit whose message contains `[phase1-full]` starts the sharded full-history acquisition.
- A commit whose message contains `[phase1-repair-batch]` runs only the exact incomplete-month queue in `docs/phase1-repair-queue.json`, serially.
- A commit whose message contains `[phase1-exact-gap-batch]` runs only the explicit missing chunk list in `docs/phase1-exact-gap-queue.json`, after freshness and intervening-acquisition guards pass.
- Do not use the full trigger until the main-branch cloud smoke and private-bucket observation gates pass.

**Initial full-history trigger issued:** 2026-08-22 after the first main-branch OIDC cloud smoke PASS and independent private-bucket observation.

**Manifest-idempotency smoke re-run:** 2026-08-22 against Edge Function version 3.

**Post-throttling hardening smoke:** PASS on 2026-08-22 after PR #7 merge. Four fresh Edge Function v3 PUT requests returned HTTP 200 for the existing EUR/USD smoke raw+manifest objects.

**Serialized monthly recovery trigger issued:** 2026-08-22 after the hardened six-day source smoke, all-pair golden sample, Python tests, and post-hardening main-branch cloud smoke all passed.

**Exact repair-batch trigger issued:** 2026-08-28 after PR #10 merged at `db0dfc592da9dd7da1fe398bc1701c5036bb1281`, with unit tests, all-pair golden sample, and bounded network smoke all passing on the exact PR head. Immediately before trigger, the frozen Phase 1 audit remained 11,667 / 25,500 manifests present, 13,833 missing, across 121 incomplete calendar months. The batch queue repairs only those 121 months with one Dukascopy runner at a time.

**Repair-batch trigger reissued:** 2026-08-28 after the first trigger run was cancelled before job creation while the PR-merge cloud-smoke still occupied the shared Phase 1 concurrency group. That cloud-smoke completed successfully at 12:32:57 UTC; the exact 121-month queue and 13,833-missing audit were unchanged before this reissue.

**Duplicate pending trigger neutralization:** 2026-08-28 after run #11 was confirmed as the active 121-month repair batch and run #12 was found pending behind it. This ordinary no-tag trigger intentionally replaces the duplicate pending batch in the shared concurrency group; after run #11 finishes, it may execute only the bounded one-day cloud smoke instead of replaying all repair months a second time.

**Exact-gap execution safety:** a fresh plan is not sufficient by age alone. Before any exact-gap source request, the workflow pages the `phase1-full-acquisition` run history and rejects the plan if another source-capable run was updated after the plan audit. The current exact-gap run and push-triggered `[phase1-no-source]` runs do not invalidate the plan. Manual `workflow_dispatch` runs remain source-capable even if their underlying head commit contains `[phase1-no-source]`.
