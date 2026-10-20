# DEC-1794 — Refresh FMP project-state draft and CI handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2040 at `93a0dc6908b17a06a8aa3229c56610152622335a`.

The canonical `docs/project-state.md` front matter still referenced only October 19 draft PRs #1994–#2005. This updates that status narrative to October 20 without altering phase or authorization. The newly verified exact-head CI says PR #2034 full historical/general FAILED (2 presentation failures), followed by passing Phase3 and full historical/general at #2035–2037. PRs #2038–2040 passed Phase3 but full historical/general was still in progress as of the checkpoint; no inferred PASS.

The current Phase8A method remains **DEC-469/DEC-268 annual-first discovery**, accepted units through 2022/run384 only, 2023/run385/attempt1 BLOCKED. Read-only GitHub main observation remains `53e203...`, `protected:false`, zero repository rulesets (including a read-only parent-inclusive enumeration returning zero), with the authoritative branch-protection API inaccessible to this integration (403). This public observation is not independently authenticated, durable no-bypass admin protection. No source-of-truth phase gate or human execution/trading approval is changed.

This is a documentation-only refresh, **not** a test-count increase (6,576 proposed source-defined tests on the latest code head) and not a source-of-truth amendment to trading rules, phase order, security enforcement, cost assumptions, or protected-data boundaries. All PRs remain drafts. No protected annual read or dispatch, branch/workflow/ruleset mutation, broker order, demo/live operation or trading; issues #779/#820/#821 still BLOCKED. CI on this exact documentation head and independent review required.
