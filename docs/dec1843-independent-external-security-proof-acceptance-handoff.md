# DEC-1843 — Owner-ready independent proof acceptance handoff for protected 2023 annual research

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent documentation-only child of #2089 at `ed6893a80ee73fd44374ea3c242297685c1668cb`. **This is an unfilled external review request, NOT evidence of approval.** All eight items are **MISSING**. It cannot authorize or consume 2023/run385/attempt1, update GitHub, install a runner, read protected history or trade.

## Current limits and authoritative blockers

- Annual-first accepted discovery evidence ends at **2022/run384**. The only next protected target would be **2023/run385/attempt1**, never a retry, rerun or replacement based on this document.
- Read-only public GitHub observation on 2026-10-20: `main` SHA `53e203133bbc141b2f48c7b8b8241d56b35166a3`, `protected:false`; parent-inclusive rulesets response empty; authoritative protection endpoint HTTP **403** to this integration. Not proof of effective inherited policies, bypass principals, continuing lock or installed runner isolation.
- **[#779](https://github.com/Dtwosam/FMP/issues/779)**: mutable-`main` check-then-dispatch allocation race. **[#820](https://github.com/Dtwosam/FMP/pull/820)**: real privileged OS isolation and publisher contract. **[#821](https://github.com/Dtwosam/FMP/pull/821)**: mutually exclusive, independently reviewed exclusive-lock versus immutable-ref alternatives. All remain OPEN/DRAFT and do not grant approval.
- Source-only reviewer outputs (`json`, `markdown`, `requests`) and saved-artifact checks, including `--verify-triplet`, can **only compare historical frozen inputs**. A local SHA-256 fingerprint is **not an independent signature or live authority witness**.

## Required independent evidence records (unfilled)

Each external owner must create an independently authenticated, dated source-bound evidence record outside this repository's disposable draft packets. Include **actual observation timestamp (UTC), principal/reviewer independence, exact repository/organization/enterprise scope, source SHA and effective rules/workflow/run when applicable, audit trail, contradictory evidence assessed, chain of custody and an explicit PASS / FAIL / BLOCKED verdict**. Never turn a field in this draft into an installed permission flag or substitute it for review.

| Exact source-defined proof ID | Required independent owner | Minimum externally verified evidence | Existing tracking review | Current status |
| --- | --- | --- | --- | --- |
| `effective_github_admin_and_inherited_ruleset_inventory` | Independent repository administrator and ruleset reviewer | Effective repo/org/enterprise protection, push/merge/force/delete permissions, all bypass/admin/Actions-write actors, timestamp and privilege scope | #779 | **MISSING** |
| `exclusive_continuous_ref_lock_and_no_bypass` | Independent security reviewer of continuous exclusive main ref lock | No-bypass `main` identity from SHA approval through server ref resolution and workflow record; concurrent permitted writer, deletion/recreation and audit cases | #779, #821 | **MISSING** |
| `independent_reviewed_source_sha_workflow_identity` | Independent reviewed SHA, source and workflow reviewer | Bound reviewed commit SHA, installed workflow blob, actual runtime SHA, selected approved action identity and provenance | #821 | **MISSING** |
| `installed_three_job_precheckout_preinstall_preaccess_enforcement` | Installed three-job preaccess gate reviewer | Installed fail-closed **before** checkout/install/protected source access for preflight, all 18 cell invocations and freeze, not merely in-job gates | #820, #821 | **MISSING** |
| `privileged_runner_os_isolation_and_publisher_witness` | Privileged runner OS and publisher isolation reviewer | Real UID/caps/mount namespace, aliases, working directory, FD 0–2/other FDs, environment/credential inheritance, publisher authority, cleanup, non-skipped adversarial tests | #820 | **MISSING** |
| `frozen_dec609_dec610_provenance_reauthentication` | Historical source and provenance custodian | Independent DEC-609/610 code/run/artifact manifests, ZIP checksums, immutable frozen predecessor 2022/run384 chain; reconcile contradictions | #779 | **MISSING** |
| `fresh_complete_authoritative_one_shot_annual_run_inventory` | Independent fresh one-shot run-inventory witness | Full current workflow-dispatch and attempts inventory; previously observed ten run numbers `{1, 376..384}` checked afresh; no 385-or-later, no missing alternate runs, immediately before any separately permitted action | #779, #821 | **MISSING** |
| `separate_2023_run385_attempt1_human_execution_decision` | Separate human run385/attempt1 decision authority | New, scoped, independent human decision **after all seven preceding evidence packages** plus irreversible failure/no-retry and specific one-shot action review | #779, #821 | **MISSING** |

## Decision boundary: two *unselected* dispatch admission paths

**Path A — exclusive server-side main lock.** Independent admins must demonstrate effective no-bypass enforcement across the entire interval from reviewed commit through `workflow_dispatch` server-side branch resolution and run record; prove no possible concurrent merge/push/force/delete/recreate/admin/Actions-write bypass; review the exclusivity and rollback/failure story. A one-time `main == SHA` check is insufficient.

**Path B — separately approved immutable-ref amendment.** Independent owners must first review/test an explicit source-of-truth and installed workflow/runtime change to admit exactly a vetted immutable branch/tag selection under correct GitHub dispatch API semantics. Historical `GITHUB_REF=refs/heads/main` requirements, commit-hash validation (syntax versus vetted identity), all three jobs and run allocation admission require re-review. Neither arbitrary SHA dispatch assumptions nor `concurrency` queues solve the one-shot race. **Do not install, tag, merge, dispatch or change policy from this draft.**

Both paths remain **UNSELECTED / NOT APPROVED**. Successful ordinary CI cannot prove a real no-bypass lock, privileged OS isolation, complete inventory or a qualified human decision.

## Runner/one-shot hard stops before any separately scoped decision

The real runner review must witness a trusted staging / OS-restricted consumer / trusted uploader boundary with genuinely read-only source/input, separated output/scratch and narrow publisher rights; a read-only GitHub token alone does not make a checkout filesystem read-only. Check real kernel namespaces, UID/caps/sudo/no_new_privs/seccomp where applicable; cwd, descriptors, symlink/mount aliases, environment keys without disclosing secrets, pre-access admissions and failure cleanup. No root-only synthetic skips count as independent PASS.

A qualified inventory custodian must reauthenticate the DEC-609/610 artifacts and complete ten-run history and prove **unconsumed 385** at the actual decision point. A human decision is **separate** and must identify exactly 2023/run385/attempt1, reviewed source, installed workflow, exclusive dispatch principal, nonretriable failure protocol, and its own validity window. If any observation is stale, missing or contradictory, verdict **BLOCKED**, with **no dispatch or retry**.

## Acceptance and release state

Every external signoff: **MISSING**. Every independent source/protection/runner/inventory proof: **MISSING**. Approved ref-lock remedy: **NONE**. One-shot run385/attempt1 human permission: **NONE**. Protected 2023 and later annual research, cross-year economics, Strategy V1, shadow, demo, Phase10, Phase11 real-money/broker operations: **BLOCKED**.

No edits in this PR change installed GitHub workflows, permissions/rulesets/ref, runner, sensitive data, broker state or capital. Human reviewers must submit evidence through their independently controlled process; code or documentation review here cannot self-approve. 
