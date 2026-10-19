# DEC-1721 — Independent administrator witness handoff contract for run 385

**DRAFT / NEVER MERGE / NEVER PROMOTE — SOURCE-ONLY PREPARATION.** This document requests independently sourced evidence. It is not an evidence packet, an approval or an instruction to unlock/dispatch the 2023 annual catalogue. Required source-of-truth: DEC-613, DEC-620, DEC-624/625/626, DEC-650/#820, DEC-651/#821 and issue #779.

## Current decision

The existing public read-only branch observation showed `main` commit `53e203133bbc141b2f48c7b8b8241d56b35166a3`, `protected=false`, with public repository rulesets reported as `[]`. This snapshot does not authenticate a future main freeze, does not cover inherited rulesets or administrative bypass, and does not show that unique annual run 385 remains unconsumed now. **release_status=BLOCKED**. No source here can turn it into green.

The governing research method remains DEC-469/DEC-268 annual pattern catalogue discovery, 2015–2022 already frozen through predecessor **2022 run 384** and 2023 protected run **385/attempt 1** next. Strategy V1 has not been synthesized or frozen. Historical Phase 7 return is only a benchmark; no real earnings.

## Required independently authenticated evidence, gathered by the human operator and reviewers

**Administrator authority and enforcement (not just `protected=true`):**

- Identify the human administrator acting, the independent administration-read reviewer, and all trusted actor categories, including direct API writers, installed apps, GitHub Actions write identities, bots, organization owners and inherited-ruleset bypass principals. Do **not** upload account identifiers, token values, credentials, private policy secrets or personal data.
- Obtain timestamped GitHub **administration-read** observations of effective branch/tag rules, administration enforcement, deletions, force pushes, tag recreation, fork syncing, and every bypass principal. An API `403`, absent access, or `protected=true` alone means **BLOCKED**.
- Bind an external *reviewed expected ref/SHA/workflow source SHA/runtime SHA* that was approved **independently of** `github.ref`, `github.sha` and self-attested workflow-run output. Copying untrusted current runner values to the expected side fails.
- Continuously prove the chosen no-bypass freeze for the entire *server-side GitHub dispatch ref-resolution window*, including the interval before submission and after the runner is recorded. A static ruleset screenshot or an unkeyed JSON digest is not adequate authentication.

**Required named continuity intervals from DEC-620 (all independently observed, not just self-reported):**

- `reviewed_sha_check_to_dispatch_submission`
- `dispatch_submission_to_server_ref_resolution`
- `server_ref_resolution_to_run_record`
- `run_record_to_post_dispatch_audit`

**Required named enforcement claims for each interval (each requires real evidence, not a fake fixture boolean):**

- `lock_effective`
- `ref_updates_blocked`
- `ref_deletion_blocked`
- `ref_recreation_blocked`
- `all_bypass_paths_blocked`
- `all_inherited_rules_visible`

**DEC-613 externally owned proof checklist (all independent prerequisites, not software flags):**

- [ ] `independent_read_access_to_effective_main_protection_and_inherited_rulesets`
- [ ] `explicit_admin_approval_and_proven_no_bypass_or_concurrent_main_updates`
- [ ] `lock_applied_after_any_dispatch_controller_source_is_merged`
- [ ] `lock_remains_enforced_across_entire_server_side_dispatch_request`
- [ ] `current_main_matches_independently_reviewed_dispatch_source_commit`
- [ ] `source_runtime_and_dec609_dec610_dec611_dec612_evidence_reauthenticated`
- [ ] `exact_ten_run_history_and_unconsumed_run_385_verified`
- [ ] `separate_run385_action_decision_reviewed_before_single_submission`
- [ ] `failure_is_non_retryable_and_run_result_is_not_claimed_by_submission`
- [ ] `subsequent_2023_freeze_and_cell_results_reviewed_before_unlock`

**Workflow and runner reviewers:**

- Pin the exact installed workflow Git blob (`09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1` only as historical installed source) and actual 2023 runtime source. Review precheckout **job-level condition** in `annual_preflight`, `annual_cell`, `annual_freeze`, then preinstall ref/SHA check, then preaccess postinstall check. The existing workflow has no precheckout `jobs.<job>.if` and checks main **after** checkout.
- Provide actual runner-host isolation, mount/UID/namespace, descriptor, artifact publisher, cleanup and negative failure-path evidence. Source-only synthetic proof, container test skips, and generic CI passing do not meet DEC-650.
- Freshly authenticate full annual-run history, the 2022 run384 frozen predecessor, run385 still unconsumed, exact workflow/runtime identities and full accepted EXP-044 artifact fingerprints. The frozen historical last-read ten-run inventory is not a live check.

**One-shot authorization remains separately gated:**

No witness document authorizes a run. After all preceding conditions are independently accepted, a different explicit human decision must approve *exactly* **2023/run385/attempt1**, tied to the frozen ref and immutable work packet. An ambiguous/failed submission, wrong SHA or partially created run is terminal; **no retry, rerun, replacement or attempt 2**. The accepted run itself must then prove all **18 cell jobs** plus preflight, freeze and artifacts. Later years remain separately gated. No automatic Phase 8B, demo, Phase 10 or live Phase 11.

## Non-authorizing human-review disposition record

This section is a template only; nothing is filled or certified by this PR.

| Evidence item | Reviewer to supply independently | Status |
| --- | --- | --- |
| Authenticated reviewed ref/SHA and source/runtime pins | independent security reviewer | **MISSING — BLOCKED** |
| Effective admin/no-bypass rule and principal inventory | repository administrator + independent admin-read reviewer | **MISSING — BLOCKED** |
| Continuous lock witness across every named interval | administrator + independent witness | **MISSING — BLOCKED** |
| Installed three-job job/preinstall/preaccess guards | workflow security reviewer | **UNINSTALLED/UNVERIFIED — BLOCKED** |
| Actual runner OS isolation and artifact publisher | privileged runner reviewer | **UNVERIFIED — BLOCKED** |
| Fresh predecessor/run-385 inventory | annual research custodian | **UNVERIFIED — BLOCKED** |
| Separate explicit exact action decision | distinct human approver | **NOT GIVEN — BLOCKED** |

Do not submit production tokens or credentials into this document, GitHub comments, test logs, or ChatGPT. Any evidence collection through private admin access belongs with authorized administrators, not this offline-only draft.

## Review rule

This template **cannot verify** authenticity, continuity, administrator privileges or GitHub's server-side ref-resolution transaction. It is intentionally incapable of producing an `AUTHORIZED` or `READY` decision. If any item cannot be independently established, remain **BLOCKED** and do not dispatch. Do not create or modify GitHub branch/tag/ruleset, install a workflow, read protected historical artifacts, retry a run, promote strategy, operate a broker, or trade on the strength of this document.

Source references: `docs/project-state.md`, `docs/phase8a-2023-run385-admin-lock-handoff.md`, `docs/phase8a-2023-run385-three-layer-ref-sha-admission-model.md`, `docs/dec1715-run385-owner-remediation-brief.md`.

**No protected 2023 research, next-year runs, synthesis, shadow/demo or live execution is authorized.**
