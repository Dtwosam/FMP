# DEC-1460 — Reviewed CI source equivalence, failures and independent annual controls

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit documentation-only child of #1683 DEC-1459 at 637c9fbf4a6f164a71b543356f4bb89ae77deba1; the **1,855 proposed source-defined methods are unchanged**.

## Distinct CI identities

Github Actions `pull_request` workflow metadata for the current draft lineage reports the *PR branch head SHA*, but runner checkout logs show `refs/remotes/pull/<PR>/merge`: a separate, generated merge **commit SHA**. A head-associated CI result is therefore **not itself a direct standalone branch-head checkout**. Git commit source trees have been shown equal for checked instances, including PR #1664:

- PR head `7eb566a3448f9fc01ed6a1433714304c19e4568c`; generated merge `5857e06c3cff50243d2ad87c31c55e86a636ea50`; common source Git tree `3ba450896e89baad327a73ca4523b5e0db298ad1`. Historical/general run `38980012458` and Phase3 acceptance run `38980012679` checked out that generated merge. Phase3 code_commit and its uploaded acceptance-artifact name were stamped by merge SHA, not head.
- PR #1665 historical runner fetched merge `d637cda910a15b693cd1b8199ac483e5e133d802`, whose Git commit parents were its immediate prior branch SHA and head `f2459aaecc9c9641fae04c7263f3549e51ff20bc`; both merge and head had identical source tree `0abe58df5b789c999ccf40c5f5362efcca7ff90b`.

The new offline reviewers through DEC-1459 require two distinct completed PR CI workflows, both run-specific actual checkout logs, the same immutable fetched full PR merge SHA, a common source tree with head, valid parent-child Git trees and byte hashes for changed tests/docs, Phase3 acceptance-index/artifact labeling, and exact per-job log receipts. These check **consistency of caller-supplied snapshots**, not independent GitHub provider attestation. The logged facts above apply to the specifically inspected PRs and must not be extrapolated as independently inspected run logs for every other PR.

## CI status snapshot at this handoff

Read-only GitHub Actions queries show both Phase3 and full historical/general suites **success** for corrective drafts #1673, #1674, #1675, #1676 and #1677 at their own head-associated PR workflow runs. Original failure #1668 (and subsequent #1669, #1670, #1671) is retained: a synthetic negative test referenced the old placeholder `"d"*40` instead of the computed subtree SHA, raising a KeyError. DEC-1449 in child #1673 corrected the fixture without altering original failed runs.

The new #1678–#1683 source drafts have their Phase3 successes where completed but historical/general workflows were **in progress** at the snapshot. Do not count them as fully verified until *their individual exact head-associated PR merge-source-tree* CI jobs actually complete successfully. This handoff draft itself requires its own Phase3 and historical/general CI and qualified review. No direct standalone-head CI checkout or immutable annual execution attestation is asserted.

## Independent protected annual gates — still BLOCKED

- **DEC-650 / #820:** independent OS/runner/storage proof of actual protected historical original **no-write** remains outstanding. Passing CI checks, synthetic fixture hashes, model/unit tests, and Git tree reviews are not OS confinement evidence.
- **DEC-651 / #821 and #779:** immutable exclusive server-enforced ref/SHA, bypass exclusion, and atomic pre-allocation one-shot 2023 **run385/attempt1** dispatch admission remain outstanding. A late in-job SHA guard, mutable `main` check, or green CI is not pre-dispatch authorization.

A fresh read-only main check still reports `53e203133bbc141b2f48c7b8b8241d56b35166a3`, branch protected=false, zero repository rulesets; the annual installed workflow blob at `.github/workflows/phase8a-annual-pattern-catalogue.yml` remains `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`. These facts are not a full organization-level privilege/bypass inventory. Both #820 and #821 remain open draft unmerged; #779 remains open.

## Strict no-go

No protected annual dispatch, attempt, retry or replay, no read/write of original protected source/archive, no annual YAML or GitHub security-policy changes, no draft merge, strategy promotion, production deployment, broker connection or real trading. Continue with only controlled one-commit tests/docs draft descendants and independent reviewed CI.
