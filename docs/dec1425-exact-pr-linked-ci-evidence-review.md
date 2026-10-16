# DEC-1425 — Exact PR association for offline two-suite CI evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit test/docs child of #1648 DEC-1424 at a27209faee57dee1a8718aa60b15bb027873cfa7. Eighteen added source-defined test methods, **1,499 proposed methods** in the draft lineage.

The earlier DEC-1422–1424 offline reviewer verifies two completed successful pull-request workflows at a SHA, with reviewed workflow IDs/paths, first attempts, positive unique run IDs and run numbers. However, the full GitHub REST workflow-run objects also expose repository, head_repository, head_branch, and pull_requests associations that bind them to a particular open one-commit draft PR. Matching only a SHA and workflow name does not fully describe the intended draft lineage.

This addition checks caller-supplied *full* run objects and a separate PR metadata snapshot. It requires matching current PR number, SHA, parent base SHA, draft branch, repository and head repository, exactly one PR link per workflow and one-commit open draft state. Synthetic negative fixtures exercise stale heads/bases, wrong PR, foreign repository, missing/duplicate associations, altered branch and malformed types. The observed current GitHub run metadata for #1648 provides an example of these full fields; this fixture is not a real signed snapshot of them.

The pure stdlib tests perform no network or GitHub API calls, and no annual workflow, trading service, data, archive, or protected source is imported or executed. The caller is responsible for obtaining and independently authenticating full GitHub records. A consistent fixture result **never** authenticates server-side dispatch reservation or proves OS-protected original no-write.

Own exact-head Phase3 and full historical/general CI plus qualified independent review remain required. Original failed draft SHAs remain failed. DEC-650/#820 and DEC-651/#821/#779 remain BLOCKED. No protected 2023 run385/attempt1 dispatch, retry, repo setting/ruleset/branch change, merge, deployment, broker or trading.
