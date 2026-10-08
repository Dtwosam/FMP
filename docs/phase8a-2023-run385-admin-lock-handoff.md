# Protected 2023 annual catalogue: administrator lock handoff

**Control:** DEC-613 / issue #779. **Status:** READ-ONLY PREPARATION; NOT A DISPATCH APPROVAL.

## Why this handoff exists

The Phase 8A governing research method remains annual pattern catalogue discovery (DEC-469/470), not any particular pattern tool. The single prospective protected 2023 execution slot is annual run **385 / attempt 1**, segment **2023**, with predecessor successful **2022 run 384, id 37663157285**. It has **not** been dispatched. No strategy synthesis, broker operation, live/demo orders, real-money execution or trading is authorized.

GitHub workflow dispatch using ref main resolves a mutable branch on the server. A successful local SHA check before the API request does not guarantee that GitHub dispatches the same commit. With no retry/replacement authority, consuming run 385 on the wrong commit is irrecoverable. The original action dispatcher, PR #777, was closed unmerged due to this P1 race. DEC-611 records the blocker and DEC-612 assesses branch-lock readiness; neither dispatches.

## Immutable provenance for the administrator

| Source | Exact evidence |
| --- | --- |
| DEC-610 landing | 58d17adbaf2238b6b774cb69f0434259984d1cb7 |
| DEC-610 first-push run / artifact | 37773291427 / 11547739610 |
| DEC-611 landing | 329e467a924ec00956505355f6cc1da7a589207c |
| DEC-611 first-push run / artifact | 37778086874 / 11550716769 |
| DEC-612 landing | 895b9ad311bd5159b2591dcfc8da714191574d00 |
| DEC-612 first-push run / artifact | 37791444781 / 11555414803 |
| DEC-612 ZIP SHA-256 | 48b4512002af76c4fe88a256cff8ddc558d185d18411f2f9d8fd9b32fba80bf3 |
| DEC-612 canonical JSON SHA-256 | cc89cf90e820341a48d41cdd5518105dd99f3c867c9ec43b8c7d989a2535d0c5 |
| DEC-612 readiness fingerprint | d9555c20a7d7a5a2d4bc79f9dd621e7a6d73e1ac9340cfec81348dc4e5f6a787 |

The concrete DEC-612 artifact records MAIN_UNPROTECTED, lock_configuration_candidate=false, main_exclusive_lock_proven=false, dispatch_blocked=true and dispatch_action_executed=false. The current annual workflow history is exactly {1,376,377,378,379,380,381,382,383,384}, with no run 385+. These are historical observations; revalidate before any future action.

## Administrative evidence without credential disclosure

Use only a secret-managed GitHub App installation or fine-grained token with **Administration: read**, not administration write. The DEC-612 audit workflow optionally accepts the FMP_GITHUB_ADMIN_READ_TOKEN Actions secret, but never echoes/uploads it. If that token is missing or underprivileged, branch-protection and ruleset evidence becomes null, which is **blocked**, not green.

Read-only API resources for Dtwosam/FMP:

- GET /repos/Dtwosam/FMP/branches/main: exact main commit and protected flag.
- GET /repos/Dtwosam/FMP/branches/main/protection: Lock branch, administration enforcement, fork syncing, force pushes, deletions.
- GET /repos/Dtwosam/FMP/rules/branches/main: effective branch rules, though not necessarily all bypass details.
- GET /repos/Dtwosam/FMP/rulesets?includes_parents=true: inherited rulesets and bypass scopes; follow through to full rule details where needed.
- GET /repos/Dtwosam/FMP/actions/workflows/phase8a-annual-pattern-catalogue.yml/runs?branch=main&event=workflow_dispatch&per_page=100: exact annual inventory.

Never paste an admin-read token into GitHub issues, PRs, repository files, Actions logs, or artifacts. A 403/404 is a visibility failure, not permission to assume no bypass. A policy snapshot is a historical observation, **not proof** that the exclusive lock remains active throughout a later request.

## Required separately authorized operator sequence

1. **Before locking**, complete/test/review any future manual-only controller or runtime amendment under a separate decision. This handoff has no controller and cannot dispatch.
2. Independently obtain administrator approval for a freeze window with zero concurrent merges, pushes or bypass actors, including administrators, organizational rulesets, apps, integrations and direct API writers. Examine Lock branch, Do not allow bypassing, force-push/deletion restrictions and fork-sync exceptions. The generic protected=true flag is insufficient.
3. Have an administrator lock the **already-reviewed exact main SHA** after any controller source merge. The administrator, not the assessment workflow, owns the settings change. Capture timestamped authoritative protection, effective rules, ruleset and bypass evidence (never secrets), and demonstrate the lock remains enforced across the entire eventual GitHub dispatch transaction.
4. Optionally rerun the **read-only DEC-612 assessment** using an admin-read secret. Even a lock_configuration_candidate=true result is not a dispatch authorization. Verify main commit, annual workflow/runtime source blobs, exact predecessor evidence, ten completed annual runs and the absence of 385+.
5. Obtain a **new separately reviewed, explicit one-shot 2023 run-385 action decision** bound to the current main lock witness, source/runtime, artifact provenance and unique attempt. Do not treat this handoff or issue #779 as approval. If any required evidence is inaccessible or ambiguous, do not dispatch.
6. Once separately authorized, hold the exclusive main lock through the server-side request and the ensuing evidence review. Independently verify resulting run number, attempt, commit, 18 cell jobs, preflight/freeze jobs, artifact digests and frozen research results. A successful submission is **not** a successful annual freeze. Never retry, rerun, or replace a failed, ambiguous, cancelled or mismatched one-shot execution.
7. Unlock only under a separately reviewed release gate. Nothing here authorizes run 386+, later years, cross-year comparison/results, Strategy V1 synthesis/promotion, Phase 8B, demo/live orders, broker mutation, real money or trading.

## Reproducible local handoff

The offline read-only script scripts/phase8a_annual_pattern_catalogue_2023_admin_lock_handoff.py uses a verified DEC-612 JSON artifact, fresh read-only main and annual history snapshots, and an expected head SHA. It rejects altered DEC-612 provenance, changed frozen source blobs, shifted main or consumed run 385. Its output includes a deterministic fingerprint and required_human_proofs checklist. It **always** records dispatch_blocked=true, admin_evidence_gathered_by_this_packet=false and all execution/trading authorities false.

**Next external gate:** HUMAN_ADMIN_EXCLUSIVE_MAIN_LOCK_WITNESS_AND_SEPARATE_DISPATCH_DECISION. The run-385 executor remains uninstalled and unarmed.

## DEC-614 concrete first-push archive (verified 2026-10-08)

The read-only artifact freeze is now complete. PR #782 merged at `ab7c5b34889e666ce14b8a00d572bcd0a07fb2cf`; first-main-push workflow run `37799674451` (attempt 1, successful) generated artifact `11559788794`, ZIP SHA-256 `52f2c02a3ac8002c2f8b7d043080bcf47292e36f9574e9d37bcce2fb93d4f11d`. Internal `dec614-2023-admin-lock-handoff.json` canonical SHA-256 is `7e470b83d4b9a04017955835ff412aa07a0a7dc91b2193b350354bbbf659a267`, and its independently recomputed handoff fingerprint is `6376c28695301ff68e44d2c353c47421c5f2a0b1574310ccf39e5508ae5ca3c0`.

The artifact records current main unprotected, human/admin proof **not gathered**, and the exact remaining checklist. It does **not** prove an exclusive lock, does not approve one-shot annual run 385, and has no write/trading permissions. The ten prior annual runs remain frozen, with run 385 unconsumed. Administrator action under issue #779 and a separate action decision are still necessary. Never treat this packet as dispatch authorization.
