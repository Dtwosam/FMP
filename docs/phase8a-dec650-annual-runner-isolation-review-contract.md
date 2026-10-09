# DEC-650 — Actual annual-runner filesystem isolation: independent-review contract

**DRAFT / NEVER MERGE. SOURCE-ONLY DESIGN. NO AUTHORIZATION.**

This document defines the *evidence required* before claiming that Phase 8A annual catalogue code can produce external reports without writing to, reparenting into, or modifying the checked-out source tree. It is based on the installed, frozen `main` source at `53e203133bbc141b2f48c7b8b8241d56b35166a3`. This branch changes **only this document**, not the annual workflow, runner, CLI, permissions, tags, rulesets, or any protected/trading material.

## 1. Frozen source facts — not security controls

Installed workflow: `.github/workflows/phase8a-annual-pattern-catalogue.yml`, committed blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`.

| Job | Source lines | Current checkout/runtime | Worktree mutations or outputs that must be moved before read-only checkout |
| --- | --- | --- | --- |
| `annual_preflight` | 33–180 | `ubuntu-latest`, `actions/checkout@v6`, editable Python install, `gh api` using `GH_TOKEN` | `.preflight/`, `.prior-freeze/`, downloaded evidence and JSON, preflight report; uploads `.preflight` |
| `annual_cell` | 182–430 | `ubuntu-latest`, `actions/checkout@v6`, 18 data matrix entries, editable Python install | `.downloads/`, `.feature/`, `.outcome/`, `.feature-evidence/`, `.outcome-evidence/`, `.result/`; uploads cell products from `.result` |
| `annual_freeze` | 432–485 | `ubuntu-latest`, `actions/checkout@v6`, editable Python install | `.cell-results/`, `.annual-freeze/`; uploads freeze evidence |

All three jobs enforce `GITHUB_EVENT_NAME=workflow_dispatch` and `GITHUB_REF=refs/heads/main`; the workflow token is restricted to `contents: read` and `actions: read`. These facts **do not** imply readonly local files, immutable `main`, an isolated user, or safe standard descriptors. In particular, a naïve `chmod -R a-w`/read-only-mount addition before current setup would break the source's intentional workspace writes; an ordinary directory mode snapshot can be reverted by its owner.

The existing test-workflow historical snapshot **intentionally hides** the installed annual YAML from the mutable working tree before running unit discovery; DEC-646's corrected `git show HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml` is committed-source inspection, *not* evidence that a workflow is installed or a mount is read-only.

## 2. Required threat model before implementation

Reviewers must name which principal controls each of: host/runner provisioning, GitHub workflow file, repository ref, checkout bytes, package build, artifact downloads, trusted staging, untrusted CLI, result publisher and external-report destination.

For each principal, explicitly enumerate the allowed file-operation set, UID/GID, supplementary groups, inherited Linux capabilities, `sudo`/root escalation, mount namespace access, remount rights, network access, token-bearing environment, open descriptors, inherited `cwd`, readable aliases and writable aliases.

At minimum, the adversarial child is assumed able to run arbitrary Python in its allocated process under its *actual* credential set. Its attempts include path opens, writes, truncation, `chmod`, rename/reparent, symlink/hardlink swaps, descriptor-relative writes, directory-FD relocation, preopened stdin/stdout/stderr, proc-fd reuse, and concurrent parents changing namespace objects. A principal retaining privileged remount, checkout-ownership, writable alias or credential escalation is **outside** a demonstrated restricted-actor boundary; such authority must be removed by a separately trusted setup, not assumed away.

A checkout mounted read-only via a bind mount alone does not prove that its underlying inode is protected from a separate writable alias or another authorized actor. Establish the full inode/namespace/writer threat model, including host-side/sibling-job writers, before claiming inventory immutability.

## 3. Candidate architecture requiring a separate implementation PR

This is a **design proposal only**, not instructions to modify or run the annual workflow:

1. A trusted setup stage checks out an exact, independently attested Git tree; verifies artifact identities/digests; installs its runtime into a separately controlled environment; and prepares dedicated writable scratch, input and external-report destinations. Staging commands with `GH_TOKEN` must finish before entering the restricted consumer, and no token-bearing descriptor/environment or GitHub credential file may be handed to it. Any download, unzip or package-install risk during setup is a distinct review item.
2. Separate the *read-only source tree*, *read-only validated inputs*, *writable ephemeral scratch*, and *external output* in an OS-enforced filesystem namespace. The untrusted consumer must have no writable checkout mount, host-visible checkout alias, writable parent allowing reparent into the source, or permission to remount/escape the namespace. Writable inputs are not interchangeable with trusted source.
3. Launch the consumer as a non-owner restricted UID/GID with cleared supplementary groups, no effective/permitted/ambient capabilities, `no_new_privs`, no root/sudo/suid escalation, and explicit network/system-call policy matched to the tested workload. The parent must close unneeded descriptors and *explicitly* attach standard streams 0/1/2 to approved safe endpoints; `close_fds=True` alone is insufficient for stdio. Review `/proc/self/fd`, `cwd`, environment, argv, umask, HOME and Python bytecode/cache paths.
4. Call annual `preflight`, `require-execution`, `require-prior-freeze`, `cell` and `freeze` in the approved isolation boundary (or independently justify a narrower trusted/untrusted split). Any CLI path currently relative to checkout must be mapped to a verified scratch/input/output directory **without changing report semantics or evidence hashes**. A fail-closed output publisher must use exclusive external creation and reject source-local paths and symlink/rename races; successful publish and no checkout mutation must be observable.
5. The trusted artifact uploader may read and upload exact accepted external results *after* the restricted child exits; its authority must not be exposed to that child. Enforce explicit resource limits, cleanup, and no retry of irreversible annual actions.

Do **not** treat this outline as a deployment recipe. It needs a separate reviewed implementation and runner-level proof. No production workflow changes are proposed here.

## 4. Reviewer acceptance matrix — all required, neither simulated nor skipped

The reviewer must receive immutable, linked evidence identifying exact commit/tree, workflow blob, runner image/kernel/mount namespace/UID maps, mount table, effective capability sets, executable and arguments, inherited descriptors, output paths, test status and any skips. Tests operate on **disposable synthetic repos** until expressly authorized for a protected workflow. Required outcomes:

| Proof | Expected result |
| --- | --- |
| Plain path create/truncate/chmod into checkout, before/after process launch | OS denial and byte-for-byte inventory unchanged |
| Same-UID attempt to restore mode 0555; privilege escalation through sudo/setuid/capabilities | Restricted actor cannot obtain checkout write authority |
| Rename/reparent external directory into checkout, including already-open directory FD | OS denial under adversarial scheduling; inventory unchanged |
| Concurrent symlink/hardlink replacement, directory reparent, writable mount alias, parent/sibling writer | Demonstrated prevention or an explicit threat-model blocker; cannot rely on post-hoc path checks |
| Opened checkout file injected as FD 1; root-only input injected as FD 0; explicit `pass_fds`; parent `cwd` or proc-fd inheritance | No unauthorized read/write capability leaks into restricted process |
| Credential canary in parent environment, arguments, files, fd, GitHub token context | Not inherited by consumer; not logged or included in report |
| Writable result output and exclusive publication *outside* checkout | Correct bytes created once; existing destination rejected; no partial-success report |
| Crash, timeout, kill, disk full, cross-device rename and failed upload | Fail closed; no hidden checkout mutation, no ambiguous retry of annual run |
| Matrix jobs and freeze job, not just preflight, with actual declared isolation | Independent evidence for all three job types and the 18 cell invocations |
| Full regression, historical pre-install snapshot, compilation, Phase 3 | Exact-source and exact-synthetic-merge pass with explicit record of root-gated skips |

A **green CI** run in which privileged OS checks are skipped does not satisfy the matrix. The DEC-644/646–649 disposable negative witnesses establish gaps; they do not certify installed annual runner behavior.

## 5. Independent dispatch/run-number gate remains separate

Even a perfect checkout sandbox **cannot** close the check-then-dispatch race in [#779](https://github.com/Dtwosam/FMP/issues/779). The currently installed workflow mandates `refs/heads/main`, while `main` is mutable. Branch protection alone, a timestamped `main == SHA` check, `git show HEAD:`, or a post-dispatch mismatch detector is **not an exclusive dispatch lock**. An immutable-ref source-of-truth change or a complete server-side exclusive lock with no bypass actors must be designed, tested, independently reviewed and **separately authorized** before annual execution.

As of the source review, `main` is at `53e203133bbc141b2f48c7b8b8241d56b35166a3`, `protected:false`, with no rulesets; the last observed annual dispatch is **run 384**, not 385. This is a snapshot, not authority.

## 6. Evidence ledger and fail-closed verdict format

An independent reviewer needs one **redacted, source-bound, immutable proof bundle per job type**; a single preflight run cannot stand in for the 18 matrix cell executions and freeze. Capture structured measurements before and *during* the restricted child, plus a final checkout-inventory digest from a separately trusted observer. A test that reads `/proc/self/status` only after the process exits, or a static `stat()` snapshot, is not a race-safe proof. The evidence publisher must never leak real credentials or token values.

Each bundle must bind at minimum these fields (the schema is an acceptance **proposal**, not installed code):

| Evidence field | Required proof and rejection condition |
| --- | --- |
| `source_commit`, `source_tree`, `workflow_blob`, `synthetic_merge` | Exact content-addressed identities; verify **raw PR source** separately from synthetic merge (DEC-646 correction disappeared from descendants despite a green parent merge) |
| `runner_identity`, `kernel`, `runner_image`, `job_type`, `matrix_coordinates` | Attested actual job/OS identity; absent/unknown values fail |
| `mount_namespace`, `mountinfo`, `source_mount`, `source_aliases`, `input_mounts`, `output_mount` | Real observed topology and read-only enforcement; any writable checkout alias or unexamined namespace actor blocks |
| `actor_uid_gid_groups`, `capability_sets`, `no_new_privs`, `seccomp`, `privilege_recovery` | Record policy and negative execution result; any sudo/remount/suid/capability recovery route blocks |
| `cwd`, `env_allowlist_keys`, `fd_0_1_2_targets`, `other_inherited_fds` | Record safe destinations and *names*, never secret contents; undefined descriptors, token-bearing handles or cwd aliases block |
| `checkout_before_after_digest`, `attempt_log`, `race_replay` | Independently observed checkout inventory and denied create/truncate/chmod/rename/FD-write operations, including adversarial timing |
| `external_report_receipt`, `exclusive_create`, `failure_cleanup` | Successful off-checkout publication, byte digest, collision rejection and no orphan/ambiguous partial result |
| `test_results`, `skipped`, `exceptions`, `independent_reviewer` | Every mandatory proof executed; any privileged skip, missing check or unresolved exception means **NOT AUTHORIZED** |

The verdict must use explicit three-way status: `PASS` only when all required checks and independent evidence pass; `BLOCKED` on any missing/skip/inconclusive result; `FAIL` when an exploit or unauthorized write is demonstrated. **Only a fully evidenced PASS** may be considered by a separate annual action reviewer, and even PASS does *not* authorize dispatch while the immutable-main and run-number gate remains unresolved. No protected annual workflow is to be executed merely to collect these experimental proofs.

## 7. Stop conditions and scope

- No changes to `main`, annual workflows, tags, rulesets, runners or permissions.
- No protected evidence reads or mutations, annual 2023/run 385 dispatch, retry, or rerun.
- No broker connections, demo/live order, real-money action, strategy promotion or Phase 8B.
- Original PRs #796–800 still need independent review; research PRs #809–819 remain DRAFT / NEVER MERGE.
- This document's PR must remain **DRAFT / NEVER MERGE**; acceptance requires an independently reviewed threat model, separate implementation, real OS-level proof and explicit annual action authorization.

**Review decision:** `NOT AUTHORIZED` until every mandatory matrix item is demonstrated on the applicable actual runner boundary, source provenance is reauthenticated, and the separate immutable-dispatch blocker is resolved.
