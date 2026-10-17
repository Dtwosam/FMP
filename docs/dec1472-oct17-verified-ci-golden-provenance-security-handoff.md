# DEC-1472 — October 17 CI-source provenance ledger and independent annual no-go

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of #1695 DEC-1471 at 959e0013c4b90c3a711e9cf1c83e0b39e6bc488c; **1,970 proposed source-defined unittest methods unchanged**.

## Exact GitHub CI evidence status, with limits

The last fully successful uninterrupted two-suite stretch starts at corrected #1680 and currently reaches **#1684** (prior #1679 original failure remains failed). Read-only GitHub workflow-run queries confirmed both required head-associated `pull_request` workflows completed/success for each PR #1680, #1681, #1682, #1683, and #1684. At #1684, reviewed Phase3 run **39028011220** and historical/general run **39028011231** both concluded success. Earlier #1678 both suites succeeded, while #1679 full historical failed due to a faulty negative fixture expected diagnostic; #1680 contained the forward-only repair and passed.

The new source-only drafts #1685–#1695 completed Phase3 successfully where observed, but their individual historical/general workflows were still **in progress** in the last recorded API snapshot. **Do not mark any of these as dual-CI-verified until its actual required tests job independently reports completed/success.** #1695 observed Phase3 success run `39029541244`, historical/general in_progress run `39029541222`. This handoff doc itself must also pass its own independent CI, which has not yet been observed here.

A green PR CI workflow's GitHub REST `head_sha` is the *PR head association*, **not proof of direct runner branch-head checkout**. Read-only log traces show checkout of `refs/remotes/pull/N/merge` for inspected PRs. For #1674 the exact source facts are:
- Standalone draft head `3033bec6416e1aeeb0fb7c41f6376d785b0ab425`;
- Temporary merge actually fetched by **both** required CI runners: `7630c183c7aca3e72a01b405b342c73db228c845`;
- Immutable Git commit object for merge has parents base `5c05f06874efed6c561103d89f443fff6be7d0a4`, head `3033bec6416e1aeeb0fb7c41f6376d785b0ab425`;
- Both head and tested merge commits have the **same Git source tree** `a122a136d6f5eb110349fd2fb02abf44ce12a37f`, so file bytes are source-equivalent for this exact inspected PR even though commit SHAs differ;
- Successful historical run `39026055632`/job `117377149221`, successful Phase3 run `39026055591`/job `117377148833`;
- Phase3 logged five deterministic scenario records and uploaded/finalized `phase3-backtester-acceptance-7630c183c7aca3e72a01b405b342c73db228c845`, artifact ID `12098433056`. Only job logs and Git objects were read: **no artifact was downloaded**.

## What was built and what it can establish

DEC-1422 through DEC-1471 add *offline source-evidence* test modules for strict draft PR and CI association, reviewed source workflow bytes, historical security regression steps, Git tree paths/modes/blob IDs, Git tree wire hash identity, both runner checkout SHA/log/provenance and actual Phase3 JSON/upload log stamps. DEC-1461–1471 extend this with detection of extra checkout actions, JSON/index schema/finite-value strictness, contradictory log stages, checkout-before-index chronology, malformed run-ID and full fifteen-input diagnostic behavior, and read-only observed #1674 golden log fixtures.

These tests require caller-supplied or static source snapshots. They do not authenticate a GitHub service or runner OS boundary, sign evidence, prove actual artifact bytes, make annual historical original no-write confinement real, or reserve one-shot workflow admission. A passing test can mean source consistency in a model, **not runtime permission**.

## Protected annual execution remains **BLOCKED**

- **DEC-650/#820:** qualified independent infrastructure custodian must witness and attest actual protected historical original data no-write isolation across all annual preflight/cells/freeze and output/uploader paths, aliases/privileges/descriptors/children. No synthetic CI replaces OS isolation proof.
- **DEC-651/#821/#779:** qualified independent GitHub administrator must prove exclusive immutable server-enforced source ref/SHA and dispatch principal with bypass paths excluded *before* allocation of irreversible **2023 run385/attempt1**. No post-allocation SHA check, mutable main ref guard, concurrency setting or green CI supplies that admission control.

Most recent separate **read-only** repository safety observations: `main` remains `53e203133bbc141b2f48c7b8b8241d56b35166a3`, branch protected=false; zero repository rulesets; installed annual workflow blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1` unchanged. #820 and #821 remain open/draft/unmerged and #779 open. This is not an exhaustive organization-admin privileges or bypass audit.

## No-go and forward process

Keep one-commit, exact-parent, open **draft** tests/docs-only children; never merge, promote, deploy, trade, alter security controls or installed annual workflow. No protected 2023 annual dispatch, retry, replay or preflight, no original protected inputs or archives, no real brokerage. Verify every new child's **own** actual Phase3 and full historical PR merge-source-tree run results. Inspect any historical failure and correct **forward only**; do not rewrite failed evidence or count pending as verified.
