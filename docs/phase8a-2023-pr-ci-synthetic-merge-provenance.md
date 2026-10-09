# DEC-633 — Offline PR CI synthetic-merge provenance classification

**DISARMED DESIGN PREVIEW ONLY.** This pure model has no GitHub client, filesystem writes, CLI dispatch path, merge action, tag/ruleset action, annual-run access, or broker/trading code. It uses fabricated Git object hashes and a nonexistent PR number; passing a fixture is not an approval.

GitHub's `pull_request` event normally checks out `refs/pull/NUMBER/merge`, not necessarily the raw source head. Workflow run `head_sha` metadata can identify the source PR head even while the checkout uses the merge commit. An operator must therefore distinguish the SHA metadata from the actual tested Git tree.

The model joins a synthetic PR record with two purported CI runs (`tests.yml` and `phase3-acceptance.yml`). It rejects any mismatch in the PR number, exact source head, base SHA, two-parent synthetic merge commit, run attempt, workflow identities, `pull_request` event, and completed-success conclusions. A passed or skipped result on a stale head cannot be interpreted as a current-head pass.

Classification is deliberately narrow:

- `REPORTED_HEAD_TREE_EQUIVALENT`: the reported source and synthetic merge **tree IDs are equal**, and the two reported workflow results match the exact PR metadata.
- `REPORTED_SYNTHETIC_MERGE_ONLY`: the reported checks and synthetic merge parents join, but the tree IDs differ; do **not** call this an identical-head checkout.
- `REJECTED`: an incomplete, stale, malformed, skipped or failed record.

These labels are **classifications of supplied metadata**, not authenticated GitHub checks, a checkout trace, an independently signed receipt, or permission to merge. This offline model neither queries GitHub nor proves the actual runner checked out that merge SHA. Independent review, the exact live workflow definition, real run/log/checkout provenance, and a post-review final ref check still must be handled separately. Even a `REPORTED_HEAD_TREE_EQUIVALENT` fixture reports `actual_pr_merge_permitted=false`, `annual_dispatch_authorized=false`, `run385_authorized=false`, and `trading_authorized=false`.

At the 2026-10-09 read-only inspection of FMP, PR #796's actual synthetic merge tree differed from its head tree because current main contributed two unchanged-in-PR paths, while PRs #797–802 had matching trees. This is a **scope-of-evidence distinction**, not a failing CI result. It is specifically unsafe to label #796's green synthetic merge checks as having tested an identical raw PR-head tree.

Official GitHub semantics:

- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target

**Unchanged:** installed annual workflow and 2023 runtime, main, historical run 385, branch protection/rulesets, original #796–800 merge train. Independent code reviews remain mandatory.

## Optional audit command — external reports only

Run only on a local **untrusted** JSON evidence file you supply, with `PYTHONPATH=src`:

```sh
PYTHONPATH=src python scripts/phase8a_annual_pattern_catalogue_2023_pr_merge_provenance_preview.py assess \
  --evidence /tmp/untrusted-pr-ci-evidence.json \
  --out /tmp/pr-ci-provenance.json
```

The command creates no GitHub connection, never executes annual code, suppresses project Python bytecode writes, refuses any output path within its **source checkout** (including symlink aliases), and refuses conflicting external report overwrites. Re-running an identical report does not rewrite the output file. Its output is **only** a classification of the supplied data with a reproducible report fingerprint; it is not an authenticated workflow receipt. It cannot authorize a merge, dispatch, run385, or trading even for a matching-looking JSON file.

The dedicated subprocess tests copy the module/CLI into a disposable checkout, force the bytecode-suppression environment variable off, run valid external reports twice, check exact checkout SHA-256 file inventories, reject checkout-local and symlink-alias outputs, reject conflicting external overwrites, and verify malformed/forged evidence does not grant authority. These tests do not cover arbitrary future filesystem races or changes to GitHub's actual event handling.
