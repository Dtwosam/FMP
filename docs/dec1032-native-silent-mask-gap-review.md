# DEC-1032 — Unchanged WD with silent native source/parent mask gaps: reviewer matrix

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of DEC-1031/#1252. Source-defined test count remains **675**. There is no observer runtime, executable test, CI workflow, protected evidence/source, production ref, runner, ruleset, permission, broker or trading change.

## Native Linux watch identity is not continuous event-mask provenance

| Draft | Actual public `inotify_add_watch` operation through a duplicated FD | Genuine kernel evidence observed on original shared instance | Independent observer's result | Implication |
| --- | --- | --- | --- | --- |
| DEC-1025/#1246 | `IN_MASK_ADD | IN_OPEN` to already registered source WD | SAME source WD and existing native `IN_MODIFY`/`IN_CLOSE_WRITE` survive; an additional source `IN_OPEN` appears on real writes | Independent instance has its normal source+parent events without `IN_OPEN` | Additive subscription modification yields *more* unexpected source events, which the unchanged parser rejects |
| **DEC-1030/#1251** | **Replace** source mask with `IN_OPEN | IN_DONT_FOLLOW` **without** `IN_MASK_ADD` | SAME source WD, but a genuine changed-byte write yields source `IN_OPEN` and named parent write events **without source-WD `IN_MODIFY`/`IN_CLOSE_WRITE`** | Separate native instance still sees real source+parent content writes | WD number continuity does not prove uninterrupted original source write coverage |
| **DEC-1031/#1252** | **Replace** parent mask with `IN_ATTRIB | IN_ONLYDIR | IN_DONT_FOLLOW` **without** `IN_MASK_ADD` | SAME parent WD, but real temporary sibling create+unlink produces **empty original/duplicate event queues**. Later a real sample write still reaches source WD but not parent | Separate native instance sees actual named sibling `IN_CREATE`/`IN_DELETE`, and normal source+parent writes | WD number and final one-name inventory cannot prove continuous parent namespace coverage |
| DEC-1015/#1236 | Explicit `inotify_rm_watch` source then re-register same inode | Original source receives `IN_IGNORED`, later new source WD; parent-only write during gap is never backfilled | Independent or surviving parent confirms intermediate writes | Removal/re-registration gap is detectable, but the gaps in DEC-1030/1031 need no WD change or `IN_IGNORED` |
| DEC-1017/#1238 | Explicit parent removal and re-registration | Parent `IN_IGNORED`, new parent WD, sibling gap, later parent events | Truly independent second parent witnesses lost sibling lifecycle | Explicit removal is not the only mechanism that can remove event categories |
| DEC-1027/#1248 | `fcntl(F_SETFL)` on a duplicate, then immediate restore | `O_NONBLOCK` status is shared between duplicate and original, unlike separate observer | Other FD retains independent status | File-description flags are separate from event-mask subscriptions and per-FD flags |

All tests operate only on newly generated, disposable public `/tmp` files and native Linux inotify instances. Mask replacement effects were reproduced in isolated disposable kernel probes. The experiments preserve original source/parent device, inode, mode, original bytes and bounded final inventory; they close all FDs. No protected annual data, production workflow or broker is touched.

The original unchanged observer must remain **`BLOCKED`** with exact `can_authorize_dispatch=false` and `independent_os_proof_verified=false` on actual unsafe streams. A missing native `IN_IGNORED`, original WD still present, restored mask or equal final digest does not establish continuous observation, independently OS-enforced protected no-write, immutable provenance, or exclusive annual authorization. An independent inotify observer in these disposable tests helps *detect* the gaps but is also not an OS write-confinement policy.

## Exact-head verification and immutable failures

- The latest **confirmed** individually two-suite CI-verified checkpoint before the new mask-replacement experiments was DEC-1026/#1247, exact SHA `60fbd8fbaf2b98f360ac4c6a58019cef97b79794`.
- DEC-1027/#1248, DEC-1028/#1249, DEC-1029/#1250, DEC-1030/#1251, DEC-1031/#1252, and this doc-only child require **their own** successful exact-head Phase 3 AND full historical regression. This reviewer matrix does not certify jobs that remain running.
- Historical failed original exact commits #1201–#1205 and #1212 stay failed. DEC-1016/#1237 at `658feef31f5a961366ff3fc8f0cc5157b704a094` also failed historical run `38420457581`, with its failed job archive unavailable (404/BlobNotFound) when inspected; do not speculate on its cause or reclassify it using downstream green results.
- Qualified independent security review remains a separate gating requirement even for fully CI-green drafts.

Independent protected OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No access to protected sources/evidence, annual run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions changes, broker/trading actions, merge, promotion, or authorization.
