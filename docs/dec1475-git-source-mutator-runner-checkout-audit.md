# DEC-1475 — Runner Git source-mutating command inventory

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit source-only tests/docs child of #1698 DEC-1474 at `fa1cabab52e547b5f0a6f4cf39749df818529b59`. Adds 14 proposed unittest methods; **1,986 proposed source-defined methods**.

## Gap and forward-only change

DEC-1461's three-stage Git checkout parser already rejected unreviewed extra fetch, checkout, reset and switch commands in timestamped runner records. It did not reject several other Git subcommands capable of changing source bytes or checkout state after the reviewed source was fetched. This child extends conservative diagnostics to `restore`, `clean`, `apply`, `am`, `merge`, `rebase`, `pull`, `cherry-pick`, `read-tree`, `worktree` and `update-index`.

The detection uses command-token boundaries rather than arbitrary word substrings, because the valid reviewed checkout log has `refs/remotes/pull/N/merge` in its fetch/checkout arguments. The pattern must not mistakenly treat that path as an independent `pull` or `merge` Git action. New tests exercise rejected additional Git mutator records and permitted read-only `show`/`log` commands containing those words in paths or flags. These are test-only synthetic log checks. A complete authentic runner log may include other shell or tool mutations not represented by timestamped runner Git commands; passing this parser is **not** a comprehensive filesystem-integrity witness.

At this handoff, #1697 and #1698 each passed both required PR merge-source-tree CI suites after the confirmed #1687–#1696 synthetic Phase3 index fixture-order failures. This child needs its **own** Phase3/full historical CI and qualified independent source review before being called verified.

**NO GO:** DEC-650/#820 actual protected original OS no-write and DEC-651/#821/#779 exclusive immutable pre-dispatch server admission for one-shot 2023 run385/attempt1 remain **BLOCKED**. No protected original/annual archive/artifact access, annual workflow dispatch/retry, installed YAML/security settings, merges, deployments, brokerage or trading.
