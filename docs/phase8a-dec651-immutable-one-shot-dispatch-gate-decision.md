# DEC-651 — One-shot 2023 annual dispatch: immutable source-of-truth decision record

**Status: DESIGN ONLY · DRAFT / NEVER MERGE · BLOCKED · no authorization to dispatch.**

This record is an independent review input for [issue #779](https://github.com/Dtwosam/FMP/issues/779). It is not an execution plan to follow before approval, a request to change GitHub settings, or authority to consume annual workflow run **385**. The branch adds **one documentation file** against the exact `main` SHA `53e203133bbc141b2f48c7b8b8241d56b35166a3`; no installed workflow, runtime gate, GitHub Actions, protected data, broker or trading system is modified.

## 1. Exact installed-source facts and irreversibility

| Source at frozen `main` | Observed property |
| --- | --- |
| `.github/workflows/phase8a-annual-pattern-catalogue.yml` · blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1` · lines 1–31 | Manual `workflow_dispatch` and input `annual_segment_label` plus `previous_annual_freeze_run_id`; token permissions `contents: read`, `actions: read` |
| Same workflow · lines 42–46, 323–327, 442–446 | Each of `annual_preflight`, `annual_cell`, `annual_freeze` separately requires `GITHUB_EVENT_NAME=workflow_dispatch` **and** `GITHUB_REF=refs/heads/main` |
| Same workflow · lines 116–119, 337–341, 456–460 | Each job invokes `require-execution --code-commit "$GITHUB_SHA"`, *after GitHub has created and numbered a run* |
| `scripts/phase8a_annual_pattern_catalogue.py` · blob `030bf98df2d5ffb50821bd0403f205c7c09f20f3` · lines 103–109 | The CLI delegates authorization to `require_historical_catalogue_execution_authorized` |
| `src/fmp/discovery/annual_pattern_catalogue_runtime.py` · blob `0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3` · lines 136–187 | Workflow run number/attempt and event input are checked; the 2023 path is gated to **run number 385** and forwarded to DEC-604 |
| `src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py` · blob `cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191` · lines 9–25, 39–47, 55–109 | DEC-604 expects **2023, run 385, attempt 1**, preceding freeze **37663157285**; `_validate_commit` checks only 40-digit hexadecimal form, **not** equality to an approved exact SHA |
| Current repository | `main` `53e203133bbc141b2f48c7b8b8241d56b35166a3`, `protected:false`, zero rulesets at latest read-only check |
| GitHub workflow-dispatch event history | Last observed matching annual run is **384**, ID `37663157285`, on 2026-10-07; **no 385 dispatch returned** in current history |

**Security consequence:** GitHub allocates a workflow run and its number before in-run shell/Python checks can reject its source, input, identity or permissions. If a wrong-ref/wrong-SHA/wrong-input dispatch occupies annual run 385, `run_attempt=1` gates and all future run-number constraints cannot repair the irreversible loss. A late `main == reviewed_sha` check is not a server-side atomic precondition of `workflow_dispatch --ref main`.

Important nuance: `GITHUB_SHA` passed to `require-execution` and checked for a valid hexadecimal shape does not prove `GITHUB_SHA == approved source commit`. Any source-verification rule must compare the actual server-selected run's exact commit/workflow tree to a separately reviewed immutable commitment before authorizing protected reads. **But an in-run comparison is still too late to preserve one-shot run 385 if the dispatch was wrong.**

## 2. Relevant platform semantics (documentation, not assumptions)

GitHub's REST API for creating a workflow dispatch accepts a `ref` that is **a branch or tag name**, and requires a credential with Actions-write permission. Its documented `ref` input does **not promise commit-SHA dispatch**, so do not assume `--ref <40-char-SHA>` is a supported immutable dispatch primitive. The workflow file must exist on the default branch to enable the event, although a dispatch may target a branch or tag.

- Official dispatch API: https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event
- Official event rules: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch
- Tag/branch rules: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- Concurrency behavior: https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency

GitHub rulesets can restrict ref **updates/deletions** but support **bypass permissions**. A protected name is not synonymous with an immutable ref for every privileged actor or with an exclusive dispatch lock. A ruleset can also be changed by authorized administrators; an owner/admin-trust boundary and configuration freeze need explicit evidence.

GitHub Actions `concurrency` controls simultaneous *running/pending* jobs, **not admission of the original dispatch** or its run-number allocation. Default pending-run replacement, optional bounded queueing, unexpected ordering and cancellations are unacceptable substitutes for one-shot admission control. The 2023 pipeline's existing internal `max-parallel: 3` for cells is unrelated to this issue.

## 3. Two designs requiring separate review and explicit selection

### Option A — stay on `main` with an *actually exclusive* control-plane freeze

Keep all three `refs/heads/main` checks; *before any one-shot request*, a separately authorized repo/organization owner must prove a server-enforced, live freeze of `main` effective continuously from source review **through GitHub accepting the dispatch**. This means enumerating all actors with permission to push/merge/force-update/delete `main`, modify branch/ruleset policies, invoke bypass, and submit workflow dispatches through REST/CLI/UI/apps. The reviewed lock must exclude or bound *every relevant bypass actor* and provide non-post-hoc evidence that updates to the ref could not race.

Even if all `main` writers are excluded, **a different workflow-dispatch actor may consume run 385**. Admission control therefore also has to reduce the population of authorized workflow dispatchers to the single approved controller during the entire one-shot window. A read-only branch protection flag, a polling watcher, a just-in-time HEAD comparison, `GITHUB_SHA` in an in-run job, and audit logs viewed only after submission **do not** independently solve the race.

**Decision:** BLOCKED. No proven GitHub-side atomic `check(ref == SHA)+dispatch` transaction or exclusive freeze with audited non-bypass actors exists in current evidence. Merely creating a main branch ruleset without independently confirming all bypass/admin/Actions-write paths cannot qualify.

### Option B — migrate source-of-truth to a protected *immutable release ref*

Prepare **a separate implementation PR** (not part of DEC-651) so all three annual jobs and runtime gate accept exactly **one independently reviewed tag ref** for 2023, with the tag's resolved commit and Git tree checked against a separately frozen approved SHA; reject `main`, all other branches/tags, changed input, unexpected run number, attempts, or predecessor ID. Never silently broaden the existing event guard to an arbitrary ref.

The tag must be protected from creation conflicts, retargeting and deletion by a reviewed, enforced tag ruleset or stronger signed/attested immutable mechanism. Examine all ruleset bypass principals and ability to edit ruleset configuration; use an independently verified attested tag-to-object mapping, *not merely the human-readable tag name*. The GitHub default branch requirement for workflow existence and source selection must be proven in the target repository. Even an effectively immutable ref does **not** eliminate a second dispatcher who can consume run 385 by submitting a different event first: separately enforce single-actor dispatch admission and one-shot ownership outside the runner.

This path has a valuable source-integrity property: the reviewed reference is not the moving `main` branch. It still needs end-to-end syntax/semantics tests for the ref migration, the 2023-only run identity, all three jobs and artifact provenance. It also requires independent code review, separately authorized source/ruleset/tag changes, and an explicit irreversible annual action decision. **No tag is created or protected and no workflow code changes are made by DEC-651.**

**Decision:** CANDIDATE ONLY, not approved and not proven feasible under the present GitHub permissions.

## 4. Rejected shortcuts

| Shortcut | Why it cannot admit run 385 |
| --- | --- |
| `git rev-parse main` / GitHub branch API equality check before `gh workflow run --ref main` | Server resolves mutable `main` *after* the read: race |
| `GITHUB_SHA` or a Python authorization check inside preflight/cell/freeze | Work executes **after the unique run number has been assigned**; rejection cannot restore 385 |
| Pass an arbitrary 40-hex SHA in `--ref` | GitHub's documented dispatch input is a branch or tag name; unspecified SHA behavior cannot be relied upon |
| Standard protection or tag rules without enforced deny/bypass audit | Privileged actor may update/retarget/delete or amend protection before or during dispatch |
| `concurrency` or a single-run environment | Schedules or cancels admitted runs; cannot atomically bind the one-shot run number to an approved commit |
| One-time post-dispatch `head_sha` check and failure notification | Detects wrong commit **after** the irreversible run-385 allocation |
| A merely write-protected checkout, DEC-650 OS sandbox, or successful #817–820 CI | Filesystem integrity is a separate security boundary; does not freeze `main` or admission to Actions |
| Submit a harmless 'test' annual dispatch to verify behavior | The test itself may irreversibly consume 385; no dry-run or retry is authorized |

## 5. Reviewer acceptance matrix — BLOCKED unless every mandatory proof exists

**Before any change proposal can be approved**, an independent reviewer must receive this bounded evidence:

1. **Principal inventory:** all users, teams, apps, tokens and GitHub automations capable of updating selected ref, changing branch/tag protections, bypassing them, dispatching this workflow or rerunning it, with current GitHub enforcement and expiration/revocation behavior. Missing principals → BLOCKED.
2. **Immutable source-of-truth:** exact reviewed source SHA, tree SHA, workflow blob SHA, explicit allowed `GITHUB_REF`, `GITHUB_SHA` and job identities for preflight/18 cells/freeze, plus a verified server guarantee that the selected ref cannot resolve elsewhere at dispatch. In-run-only checking → BLOCKED.
3. **Single-authority one-shot admission:** a server-backed or administratively enforced exclusive admission boundary preventing *any other eligible actor* from allocating workflow run 385. A client-side lock, local mutex or prior-history read without enforcement → BLOCKED.
4. **Run provenance and historical chain:** signed/independently checked source and 2022 predecessor run `37663157285`, expected **2023/385/attempt 1**, exact current workflow run history and no 385+, unchanged critical source/artifact SHA digests. Absence of data or competing attempt → BLOCKED.
5. **Failure behavior:** no preflight dry-run to learn whether one-shot dispatch will work, no automatic retry, no rerun, no replacement attempt or call after ambiguous network response; investigation remains read-only until a new explicit authorization.
6. **Control-plane change governance:** changes to workflow source, release-ref identity, rulesets, dispatcher permissions or runtime gates must be a separate change set, independently reviewed with exact merged commit and fresh CI. No ad hoc GitHub Settings changes while the lock is being evaluated.
7. **Independent OS boundary:** simultaneously satisfy [DEC-650 #820](https://github.com/Dtwosam/FMP/pull/820) on actual annual-runner filesystem, descriptors, credentials and external publication. An immutable ref does not authorize protected data access without runner isolation.
8. **Final action authorization:** after both security gates pass, request a *separate explicit approval for one irreversible annual event*. This document and a green CI badge are not that approval.

## 6. Current verdict, stop conditions, scope

**DISPATCH GATE: BLOCKED.** No safe atomic/preauthorized path to consuming run 385 is established. Evaluate Option A versus Option B in independent security review; do **not** choose or deploy a path solely based on this document.

The original PRs #796–800 still have no submitted independent reviews; all exploratory #809–821 should remain **DRAFT / NEVER MERGE**. This document adds no one-shot dispatcher, CI action, workflow privilege, production runtime, branch protection, tag, ruleset, source mutation, annual execution or broker/trading capability. Do not access protected annual data, dispatch or retry 385, modify protected refs, merge research work, promote strategies, or trade.

**Read-only exit criterion:** independently review a source- and platform-backed option with enforceable one-shot admission, exact immutable source binding, and DEC-650 OS-level evidence; otherwise remain BLOCKED.
