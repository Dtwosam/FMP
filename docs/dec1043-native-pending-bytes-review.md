# DEC-1043 — Inotify pending-byte count versus protected no-write proof

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only one-commit child of DEC-1042/#1263. There are **682 source-defined regression methods**, unchanged in this child. No executable observer, unit test, CI workflow, protected annual evidence/source, production refs, runner, ruleset, permissions, broker or trading changes.

## Distinguish shared queue counters from independent native evidence

| Native generated-public Linux control | True kernel observation | Unsafe inference explicitly prohibited |
| --- | --- | --- |
| DEC-1018/#1239: `os.dup` of native source+parent inotify FD | Original and duplicate are different FD numbers for **one** underlying kernel event queue. Reading the duplicate consumes original events; independent second instance keeps its own events | Different FD integers guarantee independent event histories |
| DEC-1038/#1259: replace BOTH original source/parent masks with `IN_ATTRIB` only | Both original WDs survive unchanged and original queue is silent on real changed-byte source writes and ephemeral sibling create+delete; separate independent witness receives native source and parent events | Existing watches and empty queue prove no write |
| DEC-1040/#1261: source write/restore plus ephemeral sibling cycle entirely during reduced dual-mask interval | Original bytes and bounded inventory **already equal** their initial state while original kernel queue is completely empty. Independent instance observed at least two actual source writes plus sibling lifecycle | Byte digests and final inventory together supply complete immutable history |
| **DEC-1042/#1263: native `fcntl.ioctl(fd, termios.FIONREAD)`** | Under full masks, both alias FDs have the **same positive pending-byte count**, and draining through either zeros both alias counts while independent FD remains positive. During dual-mask blackout, original/alias **FIONREAD=0** during a real source write and sibling lifecycle while untouched independent FD reports **positive bytes** and actual native writes, then later returns to zero when read | Zero pending bytes is independently OS-enforced protected no-write, and a duplicate FD is an independent witness |

The DEC-1042 disposable kernel probe observed 144 pending bytes on each alias before drain, and 272 bytes on the independent instance during a blind interval when alias counts were zero. Those observed **probe figures are not universal invariants**; the regression checks nonzero counts, equality of alias counts for one queued interval, actual drained byte lengths and event identities rather than hardcoding platform-specific byte totals.

All tests operate exclusively on newly generated public disposable Linux `/tmp` data and true native kernel inotify events. Final public sample and parent dev/inode/mode, source bytes, bounded one-name inventory and native descriptor closure are asserted. The separate independent Linux witness serves only as an experimental proof that events genuinely occurred during the first observer's silent interval. It is NOT privileged immutable evidence or independently OS-enforced protected write confinement.

Both the true independent unsafe event stream and a superficially clean original **empty** stream must stay **`status=BLOCKED`**, with `can_authorize_dispatch=false` and `independent_os_proof_verified=false`. Restoring original source+parent masks on the same WD integers cannot retrospectively fill a lost queue, and a later positive `FIONREAD` cannot establish continuity across earlier zero counts.

## Exact-head CI and immutable protected boundaries

- DEC-1039/#1260 at exact SHA `66fe18449dc56386af6b9a4d8f2162ecd3c50cc0` passed both Phase 3 and full historical regression.
- DEC-1040/#1261, DEC-1041/#1262, DEC-1042/#1263 and this documentation-only child **each require their own successful completed exact-head Phase 3 AND complete historical regression**. At writing, Phase 3 passed for #1261–#1262, but their historical runs and #1263's suites remained in progress. None should be called green until both suites pass. Qualified independent security review remains another distinct gate.
- Historical failed original exact commits #1201–#1205, #1212 and DEC-1016/#1237 stay FAILED regardless of descendant success; #1237's original failing job log was unavailable and root cause cannot be established.
- Every descendant remains **DRAFT / NEVER MERGE / NEVER PROMOTE**. Independently OS-enforced protected no-write DEC-650/#820 and exclusive immutable annual run385 admission DEC-651/#821/#779 remain **BLOCKED**.

No protected annual source/evidence, run385 execution/test/retry/rerun/dispatch, production workflows/refs/runners/rulesets/permissions changes, broker/trading operations, merges, promotions or authorization.
