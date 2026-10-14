# DEC-1092 — Directory self-ATTRIB versus MOVE_SELF: restored identities do not restore a removed one-shot

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only one-commit child of DEC-1091/#1312 at 235b0a1fe17af4978e5b9dd47aa39481c8f58c4e. One new Markdown reviewer matrix, **713 source-defined test methods unchanged**. No observer runtime, executable tests, protected annual evidence, broker/trading or production changes.

## Two distinct real parent-inode changes with identical final inventory

| Native control | Original alternative parent-only one-shot subscription | First real public operation | Original one-shot events | Continuing independent parent observation | Later sample writes |
| --- | --- | --- | --- | --- | --- |
| DEC-1089/#1310 | IN_ATTRIB plus MODIFY, CLOSE_WRITE, CREATE, DELETE and IN_ONESHOT | Chmod the watched disposable PUBLIC directory to a different mode | Unnamed **IN_ATTRIB|IN_ISDIR**, then **IN_IGNORED** | Continuing source+parent watcher sees first IN_ATTRIB|IN_ISDIR and another after real chmod restores original mode | True sample source and named parent MODIFY/CLOSE_WRITE on changed-byte write and separate byte restoration, missed by original |
| DEC-1091/#1312 | IN_MOVE_SELF plus MODIFY, CLOSE_WRITE, CREATE, DELETE and IN_ONESHOT | Same-filesystem rename of the **watched parent directory inode** from root/parent to root/parent-renamed | Unnamed **IN_MOVE_SELF**, then **IN_IGNORED** | Continuing source+parent watcher sees first self MOVE_SELF and another upon real rename back to root/parent | True sample source and named parent MODIFY/CLOSE_WRITE on changed-byte write and separate byte restoration, missed by original |

These are distinct kernel event categories. A directory chmod changes **metadata**; a directory self rename changes its **namespace location** without replacing the watched inode. A self MOVE_SELF event is not a child MOVED_FROM/MOVED_TO pair and has no child basename or rename cookie. A self ATTRIB event in this regression includes IN_ISDIR because it refers to the directory inode itself. Both operations are **actual changes**, not non-mutating reads, even when later reversed.

Each original one-shot is a deliberately **alternative** test-only native registration, independent from a continuously registered normal source+parent inotify observer. The first matching event removes the one-shot. The independent observer positively captures the reversed metadata/namespace operation and later actual sample writes. Final original PUBLIC directory mode, path, dev/inode identity, directory inventories and sample bytes do not prove that intermediate events were absent or that a removed one-shot was rearmed.

## Runtime and protected admission boundaries

The actual unchanged disposable Linux observer scripts/dec677_disposable_inotify_events.py::_start_watch installs continuing full source+parent mutation watches, **not** the unsafe alternative IN_ONESHOT registrations exercised here. The unchanged evaluator on genuine independent sample write receipts continues to return exact status=BLOCKED, can_authorize_dispatch=false and independent_os_proof_verified=false. Quiet local disposable records are also not independent protected OS-enforced no-write proof, and cannot authorize annual dispatch.

Each exact draft must independently complete successful Phase 3 acceptance **and** complete historical regression, followed by separate qualified independent security review. At the time of this review #1308/DEC-1087 was the last consecutive both-suite verified draft (711 source-defined tests), with historical CI for #1309 and newer exact heads still pending. Older exact commits #1201–#1205, #1212, #1237 and #1261–#1267 previously marked FAILED retain that status regardless of descendants.

Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. All descendants remain DRAFT / NEVER MERGE / NEVER PROMOTE. No protected annual source/evidence, run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading actions, merges or promotions.
