# DEC-1361 — Actual annual job source / independent annual security gates reviewer checkpoint

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of #1584 DEC-1360 at `fdd30d367d49a5beec8358946626620dab099f24`. **1,000 source-defined test methods unchanged**. This review packet uses only already inspected tracked repository source, not protected annual input, installed runner policy, protected GitHub settings, production deployment, broker state or trading execution.

## Source-backed output of this draft batch

| Exact draft | New tests | Actual risk made reviewable |
| --- | ---: | --- |
| #1579 DEC-1355 | +4 | Python synthetic runner layout refuses custom hash-colliding dictionary keys at outer and child scopes before `get`/set equality |
| #1580 DEC-1356 | +7 | Audits **existing checked-in** annual workflow: three jobs start Checkout; main-only check after checkout; pip installation before execution recheck in all jobs; **preflight fetch of EXP-044 snapshot metadata before separate execution authorization**; 18 source matrix cells |
| #1581 DEC-1357 | +6 | Pins true checkout-relative CLI/writer and workflow output locations, including `.preflight`, `.prior-freeze`, 18 cell staging/output paths and `.annual-freeze`; makes naive read-only checkout incompatible with current output behavior |
| #1582 DEC-1358 | +6 | Pins checked-in 2023 DEC-604 runtime commit argument as **40-hex syntax**, not independently approved immutable SHA binding; run385/attempt1/predecessor checks and in-source flags do not solve exclusive dispatch |
| #1583 DEC-1359 | +0 | Maps concrete workflow/CLI/runtime source boundaries to the independent OS storage custodian and repository administrator workstreams in issues #820/#821/#779 |
| #1584 DEC-1360 | +5 | Pins 3-job `needs` chain, 18 cells with max-parallel 3, checkout-relative artifact uploads and crucial difference between GitHub token `contents: read` and an OS-enforced read-only checkout |
| #1585 DEC-1361 | +0 | This checkpoint, with no source runtime/control modifications |

**Total:** 972 source-defined methods at the fully verified entry checkpoint #1578; **1,000 proposed methods** at this docs-only head, including **28 newly authored methods**. The total is a count of source-defined unittest methods, not all historical test invocations, and cannot by itself prove any security gate or readiness for annual research. New drafts stay **pending until each exact original SHA has both completed successful Phase3 and full historical suites**. Never reclassify an original FAILED SHA or an unmerged superseded sibling as green.

## Independent administrator sign-off package still missing

1. **OS isolation / actual protected no-write (DEC-650/#820):** genuine protected annual source object identity, aliases, mount namespaces, independent write-freeze ownership, UID/caps/no_sudo/no_new_privs, inherited O_RDWR/mmap/dirfd/procfd and FD0–2 targets, dedicated scratch + external uploader, policy enforcement before first access, positive output publication and authenticated cleanup/lifetime. The real checkout-relative CLI write paths must be separated in a separately reviewed implementation. Privileged skips and local kernel ENOSYS are *BLOCKED*, never acceptance.
2. **Immutable control plane (DEC-651/#821/#779):** audited server-enforced exclusive mutable-main freeze with complete dispatcher/principal/bypass inventory through the actual dispatch request **or** independent approved immutable-tag redesign and retested three existing main-only job gates. Bind externally reviewed exact workflow/ref/resolved SHA **before checkout/install/evidence** in all relevant paths. `GITHUB_REF=refs/heads/main`, `GITHUB_SHA`, an internally generated matching string, `concurrency`, source-only green CI or a post-dispatch rejection is insufficient.
3. **Exclusive annual slot and action:** fresh independently authenticated predecessor/run inventory for 2023 **run385 attempt1** before any decision; distinguish current state from earlier historical inventories. Qualified independent reviewer must sign both OS and control-plane evidence, followed by a distinct explicit one-shot action decision. Ambiguous/failure/unknown future dispatch state means **terminal hold, no rerun/retry/replacement/attempt2**.

These are not boxes a synthetic evaluator can check for approval; the relevant real security and GitHub administrators must own, supply and attest external evidence. The only deliverables added by the current drafts are regression tests and reviewer documentation. All code and CLI/workflow source examined here remains **unmodified** by the new batch; the 2023 protected annual execution slot is not consumed.

**Status:** protected independently OS-enforced original no-write DEC-650/#820 = **BLOCKED**; exclusive immutable server-side 2023 run385 admission DEC-651/#821/#779 = **BLOCKED**; protected history reading, workflow dispatch, Phase 8B, strategy synthesis, demo/live orders, brokerage and trading = **NOT AUTHORIZED**.

Each new exact head still requires completed successful Phase3 and the full historical suite, plus qualified independent review before any source-test acceptance claim. No merges, promotions, protected evidence operations, annual run/test/retry/rerun/dispatch, workflow/ruleset/permission changes, production access, broker mutation or trades are authorized.
