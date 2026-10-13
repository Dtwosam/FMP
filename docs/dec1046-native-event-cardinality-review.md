# DEC-1046 — Kernel event cardinality, pending bytes and original-state restoration review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only one-commit child of DEC-1045/#1266. The source-defined test count remains **684**. No observer runtime, executable test, CI workflow, protected data/evidence/source, production ref, runner, ruleset, permissions or broker/trading changes.

## Actual native Linux receipts must not be treated as operation counts

| Native control | Real disposable-public Linux activity | Original native observation | Why it cannot authorize protected no-write |
| --- | --- | --- | --- |
| DEC-1038/#1259 | Both source and parent event masks reduced to `IN_ATTRIB` while genuine source write and sibling create/delete happen | Both WDs remain numerically unchanged; **zero inotify events**, no `IN_IGNORED`. Independent second instance sees true source/parent/sibling changes | Two installed watches and an empty buffer are not write confinement |
| DEC-1040/#1261 | During dual-mask blackout, real source BEFORE → AFTER → BEFORE writes and transient sibling create/delete finish before restoring masks | Source bytes and directory inventory match original while original queue remains **empty**; independent instance sees at least two source modifications, named parent writes and sibling changes | Equal final snapshots are not a historical audit trail |
| DEC-1042/#1263 | Native `fcntl.ioctl(fd, termios.FIONREAD)` counts pending bytes through alias and independent descriptors | Under full masks, original and dup have identical nonzero pending-byte counts; reading either drains shared queue. Under mask blackout, **both alias counts are zero** while independent queue remains nonzero | `FIONREAD=0` is only a local pending-byte measurement and cannot prove zero operations |
| **DEC-1044/#1265** | **Six genuine `os.write` calls**, source bytes changed repeatedly and then restored, with no interim queue read | A source-only `IN_MODIFY` watch gets **ONE** coalesced event; independent source+parent dual instance receives at least six source modifications and six named parent modifications | A **positive count of 1** is not evidence of just one underlying write; same final bytes are not no-write proof |
| **DEC-1045/#1266** | **Six genuine `os.chmod` calls**, mode toggles `0600` ↔ `0640`, returning to starting mode without interim queue reads | A source-only `IN_ATTRIB` watch gets **ONE** coalesced event; independent dual instance receives at least six source attribute and six named parent attribute records | A **positive count of 1** is not evidence of one metadata operation, and identical final permission bits do not mean no changes |

Inotify can **coalesce consecutive identical unread event records** (same watch, mask, cookie and name). Two independent `inotify_init1` instances with different watch masks can legitimately report different event cardinalities for the **same** public inode operations. The full source+parent watcher emits interleaving named directory events that separate otherwise identical source records. DEC-1044 also drains after every additional write, and DEC-1045 drains after each additional chmod, confirming that event timing and queue-consumption policy change how many receipts are observable.

All native probes were run only in fresh, disposable public `/tmp` directories. The draft tests verify real syscall outcomes, native buffer parsing, source/parent device/inode/mode, returned public source bytes, bounded final directory inventory and kernel FD closure. No protected evidence, production refs, brokers or trading systems are exercised.

Both an **empty** masked-event buffer and a **single nonempty** coalesced-event buffer remain nonauthorizing in the unchanged observer: `status=BLOCKED`, exact `can_authorize_dispatch=false`, and `independent_os_proof_verified=false`. Observability is not independently OS-enforced write prevention, complete per-operation provenance or exclusive immutable annual admission.

## Exact-head CI and preserved failures

- DEC-1039/#1260 at pinned SHA `66fe18449dc56386af6b9a4d8f2162ecd3c50cc0` independently passed both Phase 3 and complete historical regression.
- DEC-1040/#1261 through DEC-1045/#1266, and **this doc-only child**, must each pass **their own exact-head Phase 3 and complete historical regression**. When this review was prepared, Phase 3 had passed for #1261–#1265 but historical suites remained **in progress**; both #1266 suites had started. These pending statuses are NOT green.
- Qualified independent security review remains a separate gate after completed CI. Every PR stays **DRAFT / NEVER MERGE / NEVER PROMOTE**, even if CI eventually passes.
- Historical original exact failures #1201–#1205, #1212 and DEC-1016/#1237 remain **FAILED**. #1237's historical failure cause is not confirmed because the original job log archive was unavailable; later descendants never rewrite that result.

Protected independent OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected annual sources/evidence, run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions modifications, broker/trading operations, merge, promotion or authorization.
