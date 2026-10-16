# DEC-1402 — October 16 source-only CI / independent security readiness handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit **docs-only** child of #1625 DEC-1401 at `86d112cd1c6f2aa6ba72c78cee3ddba7cece8b8a`. Proposed source-defined unittest count unchanged at **1,278**. No protected annual data/artifact, network archive, privileged original write probe, GitHub Actions annual dispatch, real-runner installation, repository permission/ruleset/branch mutation, production strategy/broker/trading code or merge is touched.

## Exact-commit CI checkpoint, not annual acceptance

- Latest fully completed dual-suite CI observed is **#1622**, SHA `6948ddf480be880702b34c00c8751013bcd0879a`. Phase 3: **success**; full historical/general test suite: **success**, `Ran 6151 tests`, `OK (skipped=702)`.
- Original **#1613–#1616** full historical suites were **failure** from an overbroad source-test substring diagnostic misreading `path: .preflight/preflight.json` as broad `path: .preflight`. Those exact original SHAs remain **FAILED**, not rewritten. The forward-only #1617 correction and descendants **#1617–#1622** completed **success** for both required suites.
- #1623 DEC-1399 SHA `37509d5fc0d564cd634d946d4b071182ea8121fb`: Phase3 success / full historical in progress at snapshot.
- #1624 DEC-1400 SHA `6c7b20aad473e97ed1c5f574e9c346872d303fb5`: Phase3 success / full historical in progress at snapshot.
- #1625 DEC-1401 SHA `86d112cd1c6f2aa6ba72c78cee3ddba7cece8b8a`: Phase3 and historical in progress at snapshot.
- **This new docs-only child requires its own exact-head Phase3 + full historical suite**; CI green, even when confirmed, must never be mistaken for independent actual protected runner isolation or immutable server-side admission.
- Proposed **1,278 source-defined methods** are counted in the draft test corpus; the 6,151 GitHub historical/general test executions at #1622 are a **different measure**.

## Current negative control-plane observations, read-only, 2026-10-16

Authenticated GET-only `/repos/Dtwosam/FMP/branches/main` returned `main.commit.sha=53e203133bbc141b2f48c7b8b8241d56b35166a3`, `protected=false`, `protection.enabled=false`. GET `/repos/Dtwosam/FMP/rulesets` returned **zero repository rulesets**. These observations establish **missing documented repo/branch restrictions** at that snapshot; they do not inventory all org-level controls or all potential actors, and they may go stale.

`#779`, `#821` DEC-651 and `#820` DEC-650 are all still **OPEN**. Installed source runtime contains in-job `GITHUB_REF=refs/heads/main` checks, expected 2023 **run385, attempt1**, prior freeze run `37663157285`, and `RETRY_AUTHORIZED=False`. The installed runtime 40-hex SHA-shape check does not independently bind GitHub's **server-resolved** dispatch commit to a single externally approved immutable SHA before the unique run slot is allocated. **Never submit a test dispatch**, rerun, replacement or retry to see which SHA/run is assigned; that could consume the only authorized opportunity.

## Independent decision 1 — DEC-650/#820 original historical source OS no-write

**Decision: BLOCKED.** A separate qualified OS/storage/runner custodian must produce independently verifiable evidence that the *actual protected original source object* (not a synthetic temporary fixture) is immutable to the annual process from initial exec through every child, helper and uploader. Evidence needs explicit original object ID and every symlink/hardlink/mount/relative alias, UID/GID/capability/no-new-privs/mounts, inherited writable file/dir/mmap descriptors including stdin/stdout/stderr, process tree, trusted separate scratch and uploader, positive output publication, denial observations and failure cleanup, all with zero privileged skips and independent witness.

Draft synthetic tests #1599, #1603, #1621 and offline receipt #1615 identify possible FD, rename, alias and mount risks but **cannot replace real OS evidence**. Annual CLI `Path.write_text`/`write_bytes` and ordinary GitHub read-only API tokens **do not** enforce storage-level original no-write. No actual protected original was probed or modified.

## Independent decision 2 — DEC-651/#821/#779 server-side SHA/ref exclusive admission

**Decision: BLOCKED.** A separate authorized GitHub administrator must inventory every update/bypass actor (including org/repo branch/tag administrators, GitHub Apps and service accounts), implement and independently attest an **exclusive immutable SHA/ref reservation through Actions server ref resolution and allocation**, authorize exactly one server-side 2023 run385/attempt1 with no retries, and evidence the chain *before* any irreversible dispatch. A current main SHA match, branch `protected` bit, ruleset count, checked-in workflow input allowlist, CI concurrency, post-checkout code SHA check, or untrusted "approved" receipt is insufficient by itself.

Two review routes require fresh independently accepted design: (a) genuine exclusive `main` update lock covering server-side resolution and bypass principals, or (b) a separately reviewed immutable tag dispatch source-of-truth amendment with ref/SHA enforcement and unique-slot controls. **Neither was implemented, nor may either be assumed approved.** The standard workflow-dispatch ref is a branch/tag, not a casually supplied arbitrary SHA with guaranteed server binding.

## Important source findings, not observed incidents

- The installed annual **preflight** fetches four accepted EXP-044 metadata JSON responses and writes a report *before* its separate `require-execution` entrypoint; the job later attempts an `if: always()` publication of the entire checkout-relative `.preflight` directory, even if that later check fails. Draft #1613 and its #1617 forward correction characterize source order. No protected publication or data leak has been demonstrated.
- Annual source feature, outcome and evidence artifact IDs / ZIP SHA-256 literals agree across the 18 source matrix cells and the EXP-044 catalogue inventory (#1600), but repository-internal source equality is not independent original object provenance.
- Installed annual preflight/cell/freeze jobs check out and install third-party dependencies, with version-tagged Actions, before their execution rechecks (#1618/#1620); a successful in-job gate is not pre-allocation admission.
- Installed ZIP archive digest comparisons precede `unzip -q`. Synthetic-only tests #1614/#1619/#1622–#1625 illustrate distinct member path/type constraints, metadata quotas, expansion ratios and CRC. Those illustrative scanners are **not installed**, real archives were **not opened**, and no actual exploit or bypass was asserted.

## Safe next actions and explicit hold

Within the existing test/docs boundary, continue **forward-only** review, exact-head Phase3 and historical CI monitoring, and test-fixture repair. Under separately granted explicit independent authority, external OS and GitHub control-plane custodians can provide evidence, acceptance and approved design; this draft cannot grant those powers.

**HOLD / NO-GO:** No protected 2023 annual run385 attempt1 dispatch, replacement, retry, installed workflow or permission/ruleset mutation, original dataset access/write, annual artifact fetch, Phase8B, strategy synthesis or promotion, broker/real-money/trading action, merge or deployment. Green unit CI remains a source-regression result, not permission.
