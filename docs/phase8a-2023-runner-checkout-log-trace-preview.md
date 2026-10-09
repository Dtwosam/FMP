# DEC-634 — Offline GitHub Actions checkout log trace correlation (inert)

**DESIGN PREVIEW / DO NOT MERGE / NOT AN EXECUTION TOKEN.** This module does not use the GitHub API, authorize workflow dispatch, read protected annual data, modify workflow files, merge PRs, or trade.

## Problem

GitHub Actions `pull_request` run records report a source `head_sha`, while ordinary `actions/checkout` works on the synthetic `refs/pull/NUMBER/merge` ref. In PR #796 the synthetic merge's Git tree differs from the raw PR head. Previous read-only inspection of 14 completed tests/Phase 3 jobs for PRs #796–802 found the actual runner checkout commands and resulting commit SHA in each job's log; these are stronger observations than API run metadata alone.

DEC-634 adds a narrow **offline text consistency model** of that log sequence. It requires the exact timestamped `git fetch` of the declared synthetic merge into `refs/remotes/pull/NUMBER/merge`, `git checkout --progress --force` of that ref, a `HEAD is now at` line naming the expected source and base, then `git log -1 --format=%H` followed immediately by the exact 40-character merge SHA. It rejects duplicate fetch/checkout traces, unsequenced or duplicated outputs, unexpected PR ref, mismatched SHA or parent identities, failed or skipped run metadata, missing paired workflow evidence, and type/shape confusion. Both required workflow records are `tests.yml` and `phase3-acceptance.yml`.

The source-bound deterministic preview uses fabricated hashes, a nonexistent PR number and 28 adverse fixtures. Its six unit tests cover positive synthetic matching, every negative case, strict ordering, output forgery, and malformed data. The report always denies merge, annual dispatch, run385, retry, protected-data access and trading permission.

## Limits

This is **not** a cryptographic attestation, independent GitHub log retrieval, authenticated checkout receipt, review approval or a verified immutable ref. An adversary with control over a text file can forge a matching trace; the classifier only distinguishes internally coherent from incoherent *supplied text*. It should never be wired into the live runtime/admission workflow or used as approval. A source-bound SHA-256 report provides reproducibility, not cryptographic trust. The model intentionally does **not** fetch external links or write any output files.

Existing #796–800 independent-review gates and issue #779 remain open; annual one-shot 2023 run385 must remain unconsumed. No merge, protected workflow change, tag/ruleset edit, annual run or trading action is permitted.
