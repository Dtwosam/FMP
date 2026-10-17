# DEC-1447 — Phase 3 acceptance index and artifact are labeled by checkout merge SHA

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child #1670 DEC-1446 at 6dc8c96145abd95657d133a9c061fd3782546841. Adds 17 source-defined tests, **1743 proposed source-defined methods**.

The earlier DEC-1445/1446 audit confirmed real PR #1664 checks were executed from synthetic GitHub merge SHA 5857e06c3cff50243d2ad87c31c55e86a636ea50, not the draft branch head 7eb566a3448f9fc01ed6a1433714304c19e4568c. Those commits had the same Git source tree 3ba450896e89baad327a73ca4523b5e0db298ad1, so tests covered identical source bytes while using a different commit identity.

Read-only Phase 3 run 38980012679 logs independently confirm the acceptance fixture printed code_commit 5857e06c3cff50243d2ad87c31c55e86a636ea50 and five deterministic scenario names; the acceptance artifact was uploaded under name phase3-backtester-acceptance-5857e06c3cff50243d2ad87c31c55e86a636ea50 (ID 12080194915). No artifacts were downloaded. These log observations are consistent with the installed Phase 3 workflow generating evidence using GITHUB_SHA.

This new no-network, source-only diagnostic checks caller-supplied run metadata, log-extracted acceptance-index fields and artifact upload receipt against the **actual tested merge SHA**, not GitHub's PR head association field. It rejects a fixture or artifact stamped with the branch head, missing/failed/future-attempt runs, unfinalized upload, bad run association, missing scenarios and nondeterministic fixture indicators. The synthetic evidence need not be trusted without separately authenticated GitHub logs and artifacts; it is not a protected annual original data integrity guarantee.

Own head-associated PR merge-source-tree Phase3/full historical CI and independent review required. DEC-650/#820 OS-protected original no-write and DEC-651/#821/#779 exclusive immutable 2023 run385/attempt1 server admission remain **BLOCKED**. No annual dispatch/retry, protected original/archive read, artifact downloads, installed workflows, repository security controls, merge, deployment or trading.
