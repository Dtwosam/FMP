# DEC-1474 — Immutable Phase3 composite fixture failure and forward-only recovery ledger

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit docs-only child of #1697 DEC-1473 at 4d4fbbae069254fdc4da549daaa799ba3ec09f6d; source-defined method count unchanged at **1,972 proposed methods**.

## CI facts

GitHub Actions read-only observations on October 17, 2026:
- **#1685** at `0e7825d9804547677b571a4135ef238cbab4bb69`: successful historical/general run `39028432320` and successful Phase3 run `39028432274`.
- **#1686** at `781b11da3b9b6f46f9abe05a528fb5022ab40160`: successful historical/general run `39028572979` and successful Phase3 run `39028572958`.
- **#1687** at `743db7e47d09025e63104403540444c6ed55bb86`: Phase3 run `39028660748` success, historical run **39028660756 FAILURE**. Historical/general source suite recorded 21 failing tests because the composed test fixture emitted the Phase3 acceptance JSON with `protocol` first, which did not match the DEC-1462 reviewed actual-log `{"code_commit":...}` first-stage recognizer.
- **#1688** at `2c58b5bf8b3f8d5ae5d619072d8cef8c57e56b90`: Phase3 run `39028761062` success, historical run **39028760956 FAILURE**, again 21 fixture-order failures. The original code and run conclusions for both failed PRs remain unchanged.
- Draft descendants #1689–#1696 have their own independently scheduled CI; do not infer completion/success from a green Phase3 result or from their ancestor's status. Their outcomes must be verified individually.
- **Forward fix #1697 DEC-1473** commit `4d4fbbae069254fdc4da549daaa799ba3ec09f6d` corrects the fixture's Python insertion order to serialize `code_commit` first, followed by fixture_id and protocol, with two regression tests verifying the raw log index parser and upload receipt. Its own Phase3 run `39029993318` is **SUCCESS**; historical run `39029993398` was **IN PROGRESS** at this ledger snapshot. **No recovery is claimed until its own historical job completes successfully.**

CI uses GitHub's `pull_request` **merge checkout** ref; green `head_sha` metadata alone is not a standalone draft-head commit checkout claim. Exact source-tree equality is independently observed for reviewed examples including #1674, with actual dual-job golden records in DEC-1470/1471. The synthetic source reviewers do not authenticate a real runner, signed log, output artifact bytes or security controls.

## Independent protected annual gates — NOT AUTHORIZED

DEC-650/#820 actual protected-original OS-enforced no-write across the annual preflight/18 cells/freeze remains **BLOCKED**. DEC-651/#821/#779 preallocation immutable exclusive GitHub server admission to one-shot protected **2023 annual run385/attempt1** remains **BLOCKED**. Neither a successful PR merge-tree CI job, an offline synthetic reviewer nor a corrected fixture authorizes dispatch or retrial.

No protected annual run or retry, no protected original/archive access, no installed annual workflow or GitHub security setting/ruleset edits, no merges, deployment, strategy promotion, brokerage or trading. Continue only forward one-commit open draft tests/docs children with own CI and independently qualified review.
