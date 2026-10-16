# DEC-1381 — Oct 16 independent main-branch lock verification (READ ONLY)

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit docs-only child #1604 DEC-1380 at `2fc6e04ed6c1bb917d3661c7358f42ea8e0f5757`. The proposed source-defined method count remains **1,132**. This record adds no installed workflow, ruleset, branch protection, tag, GitHub Actions dispatch action, production code, annual artifact reads or trading.

## Live read-only repository settings observed 2026-10-16

From authenticated **GET-only** GitHub API calls (not a local `git show` inference):

- `GET /repos/Dtwosam/FMP/branches/main`: `name=main`, `protected=false`, `protection.enabled=false`, `required_status_checks.enforcement_level=off`, current `commit.sha=53e203133bbc141b2f48c7b8b8241d56b35166a3`.
- `GET /repos/Dtwosam/FMP/rulesets`: **empty array** (`0` repository rulesets).
- These observations agree with earlier #779 metadata and are a **new current read-only observation**, not proof of no other organization-level controls, bypass principals or complete immutable freeze. A current observation may become stale immediately and cannot substitute for an exclusive server-side admission lock.

The public source workflow `.github/workflows/phase8a-annual-pattern-catalogue.yml` still declares `workflow_dispatch`, all three jobs use a post-checkout `GITHUB_REF=refs/heads/main` check, and installed DEC-604 validates supplied `code_commit` as 40-hex *format*, not equality to an administrator-approved future server-resolved immutable commit. The 2023 run slot is uniquely defined as **run 385, attempt 1**, with predecessor 2022 run `37663157285`; it must **never be consumed as a test**. Any post-allocation SHA mismatch is too late to protect the unique run number.

## Independently reviewable alternatives (NOT IMPLEMENTED)

**A. Prove exclusive `main` pin through the server-side dispatch admission.** The independent GitHub repository administrator must inventory org/repo/branch rules and all push/merge/admin/bypass/install-app/automation principals, establish an auditable exclusive lock with no updates possible throughout exact Actions server ref-resolution, independently reverify source+run inventories, and provide a one-authority, one-shot admission trace and denial/failure behavior. `protected=true`, local preflight `main==SHA`, in-job `GITHUB_SHA`, Actions job `concurrency`, and signed claims from an untrusted dispatcher are each insufficient alone.

**B. Amend the protected source-of-truth for immutable tag dispatch.** Requires **separate preapproval and source change** to workflow/runtime gates to admit exactly one pin-verified immutable tag and support it in server-side validation; enforce tag immutability/actor inventory, bind reviewed installed source to the server-resolved dispatch SHA before job allocation and preserve one-shot exclusion. The standard GitHub workflow_dispatch API accepts branch/tag ref, not arbitrary commit SHA; claiming `--ref <SHA>` works safely is prohibited. This alternative is not approved and no tag was created.

For either architecture, **stop** if actor inventory, exclusivity, SHA binding, documented failure paths, irreversible run385 reservation, independent reviewers, original OS no-write evidence, or production runner provenance are incomplete. Never dispatch to see which run number/commit is allocated; doing so could destroy the only authorized slot.

## Independently enforced original source no-write is a separate BLOCKED gate

DEC-650/#820 requires actual protected source identity (including hardlinks/symlinks/mounts, inherited proc/dirfds and FD0–2), read-only OS/storage access from process birth through all children, distinct trusted writable scratch and uploader, no effective caps/sudo bypass, positive publication+failure cleanup, and independently witnessed real-runner proof without privileged-skipped tests. Disposable path tests #1599/#1603 demonstrate interesting Linux semantics **only on synthetic files**. No direct write, truncate, mmap or syscall was ever attempted against the real protected original.

**Decision:** DEC-650/#820 **BLOCKED** and DEC-651/#821/#779 **BLOCKED**. This docs-only CI draft is not authority to merge, install workflow/rulesets, change trading, read protected data, run/retry/reassign protected 2023 annual run 385, start Phase8B or synthesize/promote Strategy V1. Future reviewer acceptance must use independent, current external evidence under a separately explicitly authorized action.
