# DEC-620 — Unauthenticated dispatch lock interval coverage review

**Status:** offline, source-only and non-authorizing. All input is untrusted caller-supplied JSON. Neither a positive result nor a report fingerprint proves that any real GitHub administrator enforced a lock.

## Why another control is needed

DEC-619 enumerates the race: checking a reviewed commit locally and then dispatching a GitHub workflow against a *mutable* ref is not atomic. DEC-620 makes the **continuous lock claim** needed to avoid that race explicit, including the periods before and during server-side ref resolution.

It is based on the frozen annual workflow `.github/workflows/phase8a-annual-pattern-catalogue.yml`, Git blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`, and verifies the three annual jobs retain their existing main-ref guards. The last approved research was 2022 catalogue run 384 / predecessor freeze id 37663157285. Run 385 / attempt 1 is the only prospective 2023 research slot and must not be dispatched under this decision.

## Hypothetical interval claims

DEC-620 accepts four named intervals, corresponding to:

1. Reviewed SHA check to dispatch submission.
2. Dispatch submission to GitHub's server-side ref resolution.
3. Server-side ref resolution to run record creation.
4. Run record creation to post-dispatch audit.

Each interval claims all six conditions: effective lock, ref updates blocked, deletion blocked, deletion/recreation blocked, all bypass paths blocked, all inherited rules visible, and an exact matching reviewed commit SHA. A missing interval, missing positive claim or SHA change creates an explicit gap. Duplicate intervals, malformed SHA, unknown input fields or truthy non-boolean values fail validation.

An *all-positive* result means only that this offline questionnaire contains no **claimed** gaps. It cannot establish factual continuous enforcement: snapshots at discrete times, input JSON fingerprints, repository ruleset names, and self-asserted bypass absence do not authenticate GitHub's effective enforcement throughout the transaction. An actual independent administrator witness remains required by issue #779.

A tag can satisfy every synthetic claim yet remain incompatible with the currently installed annual workflow, whose three jobs require exact `refs/heads/main`. Any tag alternative needs a separately reviewed workflow **and** runtime amendment with exact code SHA/ref binding, plus independent no-bypass administrative evidence.

## Input schema

An illustrative **untrusted, incomplete** sample (cannot yield a positive lock claim):

```json
{
  "schema": "fmp-phase8a-2023-lock-witness-continuity-coverage-v1",
  "ref": "refs/heads/main",
  "reviewed_commit_sha": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "intervals": []
}
```

The all-a commit is a fabricated fixture and never a reviewed production SHA. Every interval, if present, is an object containing `interval` (one of the four labels listed above), `resolved_ref_sha` (lowercase 40-hex) and boolean keys `lock_effective`, `ref_updates_blocked`, `ref_deletion_blocked`, `ref_recreation_blocked`, `all_bypass_paths_blocked`, and `all_inherited_rules_visible`. The parser rejects any unknown keys and duplicate labels.

Read-only example:

```sh
PYTHONPATH=src python scripts/phase8a_annual_pattern_catalogue_2023_lock_witness_coverage.py assess \
  --witness-json /tmp/dec620-untrusted-claims.json \
  --out /tmp/dec620-coverage-report.json
```

The CLI refuses to write reports into the checkout, makes no network or GitHub API requests, changes no refs/branch/tag rules and never dispatches an annual workflow. An independent report validator recomputes the complete output using the pinned current source and the report's embedded **untrusted** input, so even a recomputed SHA-256 fingerprint cannot forge a positive report permission field or hide omitted interval claims.

## Release boundary

Every report keeps `witness_authenticated=false`, `server_transaction_continuity_proven=false`, `effective_no_bypass_rules_verified=false`, `exclusive_main_lock_proven=false`, `immutable_tag_lock_proven=false`, `workflow_dispatch_authorized_by_this_report=false`, `run385_execution_authorized_by_this_report=false`, `dispatch_blocked=true`, `trading_authorized=false`. It also cannot establish whether live run 385 was consumed.

The next gate must be a separately approved administrative lock witness valid through the entire server transaction, plus an independent one-shot dispatch decision. No run 385 dispatch, rerun or replacement; no 2024+ research, cross-year comparison, strategy synthesis/promotion, Phase 8B, broker mutation, demo/live order, or real-money trading is authorized by DEC-620.
