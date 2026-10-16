# DEC-1328 — Minimal Linux memfd F_SEAL_SHRINK requirement for open-time truncate denial

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit child of #1551 DEC-1327 at `a17c6b99525264a32f06283777e034a661b83777`, one native Linux generated PUBLIC anonymous memfd test and reviewer doc, proposed **885 distinct source-defined tests**.

A local genuine Linux probe independently confirmed that `os.open("/proc/self/fd/<memfd>", O_RDONLY|O_TRUNC)` is a destructive open-time **file shrink** operation. Five distinct generated PUBLIC anonymous original inodes prove exact narrow seal requirements under native genuine inode-only IN_MODIFY and retirement watches:

| Original memfd seal state | Exact syscall result | Original source |
| --- | --- | --- |
| F_SEAL_GROW only | **Success**, native IN_MODIFY | Data deleted, original length 0 |
| F_SEAL_WRITE + F_SEAL_GROW | **Success**, native IN_MODIFY | Data deleted despite WRITE seal |
| F_SEAL_SHRINK only | **EPERM** | Original bytes/length intact, no MODIFY |
| F_SEAL_WRITE + F_SEAL_SHRINK | **EPERM** | Original bytes/length intact, no MODIFY |
| F_SEAL_FUTURE_WRITE + F_SEAL_SHRINK | **EPERM** | Original bytes/length intact, no MODIFY |

Each test case authenticates original inode dev/ino, exact F_GET_SEALS, source content/size, genuine Linux syscall result/errno, and final IN_DELETE_SELF/IN_IGNORED with FD cleanup. There is **no named original parent** on any anonymous memfd. These five cases show F_SEAL_SHRINK—not a coincident write/grow bit—is necessary for the tested open-time shrink denial. This does not certify an independently OS-enforced policy on *existing protected annual filesystem files*.

Each exact SHA must independently pass successfully completed Phase3 and full historical tests, followed separately by qualified independent review; pending is not green, prior FAILED exact-head statuses remain FAILED. Protected DEC-650/#820 and DEC-651/#821/#779 remain BLOCKED. No protected annual execution/test/retry/rerun/dispatch, source/evidence, installed workflow/ruleset/permissions, broker/trading, merge or promotion.
