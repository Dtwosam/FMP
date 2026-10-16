# DEC-1350 — DEC-650/651 administrator handoff: prove storage no-write and immutable admission separately

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of #1573 DEC-1349 at `66a16e03052da63e7a5a01c9244a70c0cd63f38d`. **957 distinct source-defined test methods unchanged.** This is a plan for future independent admin/reviewer evidence, **not execution authorization, workflow code, installed controls or protected market-data inspection**.

## Confirmed governing context

FMP remains in **Phase 8A** under annual discovery-first governing method **DEC-469 / DEC-268**. Market-pattern representations, simulations and isolated OS demonstrations are subordinate tools, not independent authority to access protected annual sources or move to shadow/demo/trading. The phase is still blocked at the 2023 annual research slot. GitHub issue **#779** specifies 2023 **run 385 / attempt 1** as irreplaceable and prohibits retry, rerun and replacement if the unique slot is ambiguously consumed.

The substantive original design records have **two distinct issues**:

- **Issue #820 / DEC-650:** current annual CLI writes checkout-relative outputs, so simply changing its checkout to read-only would break staging and publication. The unimplemented review architecture is **trusted staging → OS-restricted consumer → trusted uploader**, with read-only protected input/checkout and isolated scratch/output. The non-root child must not inherit writable original handles, writable mapping, privileged credentials, mount capabilities or uncontrolled FD0–2 targets. Previous root-only negative proofs skipped on ordinary CI. The original PR's completed Phase3 and general tests prove only documentation compatibility, **not a real runner isolation deployment**.
- **Issue #821 / DEC-651 plus #779:** the installed three jobs currently use `GITHUB_REF=refs/heads/main`; dispatch's `--ref main` can resolve to a different commit **after** an earlier SHA check. The source run385 may be consumed before a post-dispatch guard rejects the change. GitHub workflow dispatch accepts a **branch or tag**, not an arbitrary raw commit SHA. `concurrency` cannot independently establish exclusive immutable admission. Design A is externally enforceable administrator no-bypass **exclusive main freeze** plus a single authorized dispatcher; design B is a separately approved source-of-truth amendment for an **immutable protected tag**, with all current main-only runtime/job gates reworked, staged and reviewed **before any dispatch**. Neither alternative is installed.

## Proposed prerequisite workstream A — independently owned protected no-write

| Required deliverable | Responsible reviewer/owner | Fail-closed acceptance |
| --- | --- | --- |
| Protected original-source inventory | Actual source custodian outside the executor | Exact real original data object/mount namespace/aliases/checkout, source provenance and all writable paths must be authenticated; generated PUBLIC /tmp or anonymous memfd is not a substitute |
| Trusted staging design | Independent operator plus source owner | Stage verified inputs and code **before child confinement**, with writes directed only to separate scratch and external publication; no child write path back into original checkout/data |
| Child OS/storage policy | OS/runner administrator independent of annual executable | Authenticated effective UID/GID, capabilities, sudo ability, no_new_privs, mount namespace, read-only original storage, symlink/dirfd/procfd aliases, inherited ordinary and standard FD0/FD1/FD2, environment allowlisted keys, no bypass/escape |
| Representative adversarial denials | Qualified security reviewer in approved disposable same-policy environment | Actual negative write/truncate/**O_RDONLY|O_TRUNC**/fallocate hole/zero/writable-map/FD alias tests with real kernel errno and **independently compared original bytes/inode**. Neither skipped privileged probe nor quiet inotify can count as denial |
| Publication and failure behavior | Trusted uploader and auditor | Only external result/scratch output allowed; positive upload path tested, no source/checkout writes, fail-closed cleanup on error and no retention of privileged writable source handles |
| OS proof ledger | Qualified independent reviewer | Timestamped kernel/mount/UID/capability/FD targets/actual original source identity, policy before earliest input access through end-of-window, separate attestation signatures and raw evidence. Unknown/bypassed/skipped = **BLOCKED** |

**No candidate container, root policy, mount change, sudo invocation or workflow installation is authorized by this design.** The current development host's previously observed Landlock `ENOSYS` means there is no verified local Landlock denial or an implicit permission to relax restrictions.

## Proposed prerequisite workstream B — immutable one-shot GitHub dispatch admission

| Required deliverable | Independent owner | Fail-closed acceptance |
| --- | --- | --- |
| A or B selection | Repository owner and qualified independent GitHub security administrator | **A:** prove continuously exclusive protected main freeze with no bypass writer over the **complete server-side dispatch interval**, not just an earlier branch SHA. **B:** separately approved immutable-tag source-of-truth amendment, and retest **all three** installed jobs against revised tag/ref semantics |
| External expected code identity | Review authority separate from runner and dispatcher | Pin exact reviewed repository/ref/resolved commit SHA/workflow YAML SHA/runtime blob and inputs **outside untrusted GitHub execution context**; `GITHUB_SHA == GITHUB_SHA` and matching synthetic JSON are not proof |
| Before-checkout admission | GitHub/repo owner | Prove actual server-side approved ref and source identity before checkout; a step running after checkout cannot guard earlier checkout |
| Before setup/install and before evidence | Runtime/workflow reviewer | Each preflight, 18-cell matrix and freeze path has tested enforced ordering, true immutable workflow/runtime binding and no metadata/source/evidence access before approval |
| Exclusive annual slot inventory | Independent reviewer, just prior to any authorized request | Fresh trusted workflow run history and predecessor evidence, no existing 385+ dispatch, exact 2023/run385/attempt1, no ambiguity/race, no wider year or retry |
| Distinct one-shot action | Explicit separately empowered human authority | A narrowly scoped approval **after both** workstreams pass with no automation creating the action. Timeout/unknown/failure = terminal hold, **no retry/attempt2/replacement** |

## Existing evidence that must never be treated as these deliverables

The new source-only synthetic `assess_synthetic_claims` test family through **#1573 DEC-1349** produces only all-`BLOCKED` diagnostic classifications. Its static code quarantine proves absence of one explicit function name in selected tracked source, not server-side workflow enforcement. Anonymous memfd seals prove syscall-specific denial on **different generated PUBLIC inodes**, not independently administered policy on protected annual storage. Named PUBLIC original+parent inotify receipts can observe data writes but miss certain mapped/anonymous kernel mutations, not deny them. A well-formed matching Git SHA-1 string remains self-reported. Fully successful Phase3/historical CI is necessary for draft quality but **insufficient** for protected source access.

## Safe next engineering milestone

Before any implementation beyond inert unmerged drafts, the owner and independently qualified reviewer must **separately supply/approve a concrete Gate A (OS isolation) design and Gate B (one-shot immutable dispatch) design**. Review documented threats, stage a fully disposable nonprotected copy of the *same intended policy*, verify real kernel denials, review actual workflow/runtime amendments independently and confirm genuine GitHub administrator no-bypass constraints. Only after a new explicit owner decision could separately scoped production control changes even be considered; nothing here pre-approves installation or protected execution.

**Current verdicts:** DEC-650/#820 = **BLOCKED**; DEC-651/#821/#779 = **BLOCKED**; protected annual run385/attempt1 = **DO NOT DISPATCH**; future-year research, Strategy V1 synthesis, Phase 8B, broker/demo/live execution and trading = **NO AUTHORIZATION**.

This exact new SHA needs individually completed successful **Phase3 acceptance AND full historical tests** and qualified independent review before even its documentation can be called accepted; earlier failed original SHA classifications are unchanged. All PRs remain **DRAFT / NEVER MERGE / NEVER PROMOTE**. No protected annual input/evidence read, annual run/test/retry/rerun/dispatch, workflow/ruleset/permission changes, production, trading or merges.
