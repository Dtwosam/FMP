# DEC-1072 — IN_OPEN + IN_ONESHOT: distinguish source lifetime, parent lifetime and production scope

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit **documentation-only** child of DEC-1071/#1292 at `c5d56e2b1898084624e883dc2953d774c924055f`. **701 source-defined test methods unchanged.** No observer runtime, executable test, production or protected-environment changes.

## Two independent ways a benign public read defeats a broadly masked one-shot

| Case | One-shot registration | Harmless first action | One-shot native receipt | Independent continuously registered evidence | What it establishes |
| --- | --- | --- | --- | --- | --- |
| DEC-1069/#1290: source-only read first | Sample source `IN_OPEN | IN_MODIFY | IN_CLOSE_WRITE | IN_ONESHOT` | Real read-only open/read/close of **sample** | Unnamed source `IN_OPEN` then `IN_IGNORED` | Later genuine sample content write/close emits source and named-parent MODIFY+CLOSE_WRITE | **Same-inode** harmless read removes all later source mutation coverage |
| DEC-1069/#1290: source writable open first | Fresh original-FD same source mask after first watch removed | Actual writable open of **sample** | Unnamed source `IN_OPEN` then `IN_IGNORED` before write | Genuine changed-byte write/close on this very handle emits source and named-parent MODIFY+CLOSE_WRITE | **Same-handle** first OPEN removes subscribed MODIFY and CLOSE_WRITE before they can occur |
| DEC-1071/#1292: unrelated sibling read first | **Parent directory** `IN_OPEN | IN_CREATE | IN_DELETE | IN_MODIFY | IN_CLOSE_WRITE | IN_ONESHOT` | Real read-only open/read/close of **public-read**, a child that is NOT sample | **Named sibling** `IN_OPEN` then `IN_IGNORED` | Subsequent actual changed-byte write/close of **sample** emits both source and named-parent MODIFY+CLOSE_WRITE | **Cross-inode** harmless read removes observation of another child's future mutation |

All operations occur only in freshly generated **PUBLIC** disposable Linux `/tmp` fixtures. The original one-shot instance and the independent source+parent instance are created with separate native `inotify_init1` calls, not duplicated descriptors. The original instance's `IN_IGNORED` is an observable watch-removal record, **not** an OS-enforced guarantee that the source could not change. Positive independent receipts demonstrate real activity while that one-shot is disarmed. Final sample/sibling bytes and dev/inode/mode plus bounded inventory do not recreate lost native event history.

## Critical production-scope distinction

The unchanged disposable evaluator helper `scripts/dec677_disposable_inotify_events.py::_start_watch` intentionally uses continuing full source+parent mutation subscriptions **without** `IN_ONESHOT` or `IN_OPEN`. DEC-1069 and DEC-1071 construct **separate alternative native one-shot registrations** to demonstrate a blind spot in the proposed *coverage inference*, **not** to allege that the current observer runtime actually installs that unsafe mask. The evaluator itself is unchanged; it returns exact `status=BLOCKED`, `can_authorize_dispatch=false`, and `independent_os_proof_verified=false` for independently witnessed write activity. Even a locally quiet full watcher remains `LOCAL_DISPOSABLE_WITNESS_UNVERIFIED`, never protected OS no-write proof or annual authorization.

Own successful exact-head Phase 3 **AND** full historical regression plus separate qualified independent security review are required for every draft. No descendant can reclassify earlier failed originals #1201–#1205, #1212, #1237 and #1261–#1267, which remain FAILED. Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**.

No protected annual source/evidence, annual run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading, merges or promotions.
