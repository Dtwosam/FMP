# DEC-1716 — Installed annual workflow blocker source contract

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent tests/docs-only child of #1962 at `ae3c7a3b32538879eca1d5b5c14310358a82cf0d`. No source-of-truth, workflow, run, security settings or execution changes.

## Purpose

The next profitable-strategy milestone is blocked upstream of new pattern discoveries: **2023 Phase 8A annual catalogue run 385/attempt 1 is not authorized** (issue #779). DEC-1715 identifies the independent external administrative owner. This source-pinned regression suite makes the *actual installed* annual workflow's insufficient guard topology machine-checkable instead of mistaking planned or synthetic guards for installed protection.

It checks the installed `.github/workflows/phase8a-annual-pattern-catalogue.yml` blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1` and twelve independent properties: the three-job structure, explicit manual inputs, read-only GitHub token job permissions, checkout-first ordering, existing main-ref-only checks **after** checkout, absence of job-level precheckout admission, runtime setup/installation **before** execution authorization, preflight metadata access **before** execution authorization, cell/freeze authorization before artifact download, and the 18-cell matrix covering three pairs/timescales and both horizons.

## Acceptance semantics and limits

A green result does **NOT** mean the workflow is secure or ready to dispatch. The test verifies that the **known blocker still exists as described**; a future separately reviewed installed amendment will deliberately require this suite to be updated/replaced against its newly pinned source. The SHA1 is Git's blob **identity**, not an administrative approval signature. Read-only `permissions:` is not read-only checkout filesystem, OS isolation, or proof of a no-bypass source lock. CI results are not economic edge.

The test imports no protected evidence or broker interface, has no GitHub API calls and makes no mutation. The current 2023 one-shot run must remain unconsumed; no rerun/retry/attempt2, 2024+, cross-year synthesis, Phase 8B, demo/live or real-money authorization is created.

**Reviewer follow-up:** independent administrator no-bypass lock or reviewed immutable-ref alternative; external authenticated reviewed SHA, early precheckout/preinstall/preaccess gate for all jobs, actual runner OS isolation; authoritative fresh annual workflow run inventory and **separate explicit one-shot decision**. Unknowns are **BLOCKED**, not passed.

Conforms to DEC-650/#820, DEC-651/#821, issue #779 and `docs/dec1715-run385-owner-remediation-brief.md`.

Only tests and documentation. Own exact-head Phase3 and full historical/general CI plus independent qualified review required; do not merge or promote.
