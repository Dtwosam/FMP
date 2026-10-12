# DEC-971 — Native automatic watch removal and additive-mask reviewer matrix

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only child of DEC-970/#1191. This is a reviewer handoff, not executable OS proof.

## Coverage cross-check

| Draft | Actual generated public Linux kernel operation | Expected native records | What remains unknowable |
| --- | --- | --- | --- |
| DEC-959/#1180 | Explicitly remove source with inotify_rm_watch | Source IN_IGNORED; parent still receives named sample writes | Source timeline after removal |
| DEC-960/#1181 | Explicitly remove parent with inotify_rm_watch | Parent IN_IGNORED; source still receives content writes | Sibling namespace changes while parent absent |
| DEC-961/#1182 | Explicitly remove both | Two IN_IGNORED records, empty later drains, FD still open | Any watchless mutation history |
| DEC-963/#1184 | Re-add source only after removing both | New source writes visible; siblings unobserved | Lost interval and absent parent coverage |
| DEC-964/#1185 | Re-add both after different-byte write/restore while watchless | No event in gap, later source writes visible | No retrospective detection of changed-and-reverted source |
| DEC-965/#1186 | Replace source mask with only IN_ATTRIB, no IN_MASK_ADD | Same source WD; direct source write mask gone, parent sees named writes | Unsubscribed source content events |
| DEC-966/#1187 | Replace parent mask with only IN_ATTRIB, no IN_MASK_ADD | Same parent WD; sibling create/delete absent, source write still visible | Unsubscribed parent namespace events |
| DEC-968/#1189 | Replace source mask with IN_MODIFY plus IN_ONESHOT | First source write produces IN_MODIFY then IN_IGNORED; parent remains live | Subsequent source events after automatic removal |
| DEC-969/#1190 | Replace parent mask with IN_CREATE plus IN_ONESHOT | First sibling creation produces IN_CREATE then IN_IGNORED; source remains live | Later sibling unlink after automatic removal |
| DEC-970/#1191 | Add IN_OPEN to source with IN_MASK_ADD | Same source WD, new genuine IN_OPEN *plus retained source content writes*, parent named writes | Runtime completeness in presence of unexpected masks |

The native flags \`IN_ONESHOT\` and \`IN_MASK_ADD\` affect registrations, not accepted source or directory write-event masks. An unchanged numeric WD is not evidence of a continuous subscription. Native \`IN_IGNORED\` is evidence of invalidation, not a benign empty interval. Adding a new mask must not be conflated with replacing existing masks. The narrow observer parser intentionally declines an unrecognized \`IN_OPEN\` event; it must fail closed rather than drop it and claim a quiet stream.

The DEC-968–970 tests each use newly generated, nonprotected public \`/tmp\` files, real Linux inotify event queues, final inode/parent metadata and inventory checks, and explicit FD closure. Neither mocked receipt assertions nor local native controls are independent OS-enforced no-write protection. There are **633 distinct source-defined test methods** at this child; the documentation-only commit adds no test methods or runtime changes.

## Separate verification gates and hard stops

Each exact-head PR must pass Phase 3 **and** full historical regression individually. No later success erases an earlier failed exact SHA. Independent qualified security review is still necessary. The existing observer exposes only \`BLOCKED\` or \`LOCAL_DISPOSABLE_WITNESS_UNVERIFIED\`, with \`can_authorize_dispatch=false\` and \`independent_os_proof_verified=false\` regardless of native records or CI.

Protected, independently OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected annual run385 dispatch/test/retry/rerun, protected evidence or sources, production refs/workflows/runners/rulesets/permissions, broker/trading operations, merge, promotion or authorization.
