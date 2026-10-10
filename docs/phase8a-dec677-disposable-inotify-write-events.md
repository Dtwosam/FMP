# DEC-677 — Disposable Linux inotify write-and-restore witness

**DRAFT / NEVER MERGE · SOURCE ONLY · No annual authorization.**

This prototype complements DEC-674 draft #845's digest-blindness counterexample. It uses a real Linux inotify watch on **one newly generated public synthetic file under fixed /tmp**. No protected annual checkout, historical artifact, GitHub workflow or broker input is accepted.

## What it demonstrates

The opt-in negative case creates a watch **before** two real flushed-and-fsynced writes (original bytes -> different public bytes -> original bytes). Initial and final bytes and SHA-256 match, but the kernel-generated event queue contains write/close-write events. The collector requires a bounded well-formed event buffer, the exact synthetic watch descriptor, no IN_Q_OVERFLOW, no IN_IGNORED / IN_DELETE_SELF / IN_MOVE_SELF, and observes two or more write-related events for the deliberate negative control. The verdict is BLOCKED, exit 2, **despite an identical final checksum**. A clean disposable case with no writes produces only LOCAL_DISPOSABLE_WITNESS_UNVERIFIED, exit 3, never PASS.

A malformed/truncated event, wrong watch descriptor, event queue overflow, watcher invalidation, missing monitor prerequisites, changed final bytes or any observed write causes BLOCKED. No raw inode paths, host credentials or sensitive data appear in JSON. Every result has can_authorize_dispatch=false and independent_os_proof_verified=false.

Default CLI is inert BLOCKED exit 2:

    python -B scripts/dec677_disposable_inotify_events.py

Explicit synthetic Linux cases:

    python -B scripts/dec677_disposable_inotify_events.py --execute-disposable-control
    python -B scripts/dec677_disposable_inotify_events.py --execute-reverted-write-negative

The **18 source-defined tests** passed in an author-local Linux run; default tests passed with the two real inotify demonstrations skipped. With DEC677_EXECUTE_INOTIFY_TEST=1 the full 18 tests passed, including both kernel cases. These are opt-in OS experiments, intentionally not normal CI acceptance.

## DEC-678 — A watched inode is not a pathname identity guarantee

A file-level Linux inotify watch is attached to the **original inode**. A writer with directory-entry replacement authority can change what the path `sample` resolves to, potentially leaving later mutations of the replacement outside that inode's original watch. A before/after byte or SHA-256 comparison may still match. In the local disposable Linux reproduction, an atomically replaced, same-content file changed the source inode and generated old-watch attribution/deletion/invalidation events; this experiment does **not** claim such events are always absent.

This stacked change pins a snapshot of the *initial* disposable regular source inode before starting the watch, then opens the final pathname with `O_NOFOLLOW|O_NONBLOCK` and compares its `(st_dev, st_ino)` with the initial identity. Snapshots reject nonregular files (including FIFOs), symlink leaf substitutions and files larger than 4 KiB. **A different final inode BLOCKS even if all report bytes and hashes match**, independently of what events happen to be observed. An explicit `--execute-inode-replacement-negative` opt-in creates a second public same-content file and atomically substitutes it for the watched one, requiring an inode mismatch and a BLOCKED exit 2. Its sibling modes continue to use the same generated temporary checkout only.

Nine additional regression cases bring the suite to **27 source-defined tests**. In addition to the prior two optional inotify demonstrations, the new real inode-replacement demonstration is opt-in and skipped in ordinary CI. Other tests exercise strict boolean identity claims, unchanged-path read, symlink rejection, FIFO nonblocking rejection, mutually exclusive negative modes and false negative-control reporting.

**Limitations remain substantive:** inspecting the pathname twice is not a continuous inode-identity guarantee against a privileged writer who swaps it out and back between observations. An attacker can mutate via other hard links, aliases or namespace changes. inotify is event monitoring, not a prevention policy or independent attestation. Even matching stable-inode snapshots and a quiet watch are not authorization for annual run 385 or evidence that the installed 20-job runner has been contained.

## DEC-679 — observe containing directory, not only the sample inode

A single-file inotify watch cannot establish that **a new sibling entry was not created** inside the monitored fake checkout. This stacked extension adds a second inotify watch on the directory holding the sample, covering `IN_CREATE`, `IN_DELETE`, `IN_MOVED_FROM` and `IN_MOVED_TO` in addition to existing file-level write/invalidation events. The bounded parser accepts only the two installed watch IDs, rejects unknown IDs or queue overflow, and separately counts directory entry mutations.

The parent also checks the fake directory's final inventory against the expected single entry `sample`. A silent or unobserved extra pathname therefore BLOCKS at the final inventory check even if the sample inode and SHA-256 match. The manual `--execute-sibling-creation-negative` mode creates a public synthetic second file **after both watches are installed**; it requires the directory mutation to be observed, the final inventory to be different and the status to be **BLOCKED**, exit 2. This cannot be used with other manual negative-control modes.

Eight additional source-defined regression cases bring this stacked harness to **35 tests**, with four explicit opt-in Linux demonstrations skipped by default. Tests cover all four directory mutation types, unexpected watch IDs, silent inventory drift, missed negative controls, mutually exclusive modes and real temporary sibling-file creation.

Even with file+directory watches, event streams are not an enforcement boundary or reliable continuous audit of privileged writers, watches can be moved/removed and buffered data may be lost, and an actor can create/delete entries between snapshots. The synthetic event collector is not an independently authenticated host observer and is **not** acceptable evidence for actual annual preflight+18 cells+freeze.

## DEC-680 — A restored directory inventory can conceal transient creation

The DEC-679 test leaves a synthetic sibling file present, so both directory inotify events and the final directory inventory reveal it. A harder counterexample is to create a new sibling file **and delete it before the final inventory comparison**. The original sample inode and bytes are unchanged, and the final directory listing again contains exactly `sample`. A before/after inventory-only method cannot establish that no directory mutations happened during the interval.

The opt-in `--execute-transient-directory-negative` creates and removes a public temporary sibling **after installing both the sample and directory watches**. The bounded directory event parser must see at least two separate `IN_CREATE` / `IN_DELETE` events, and the result is always **BLOCKED exit 2**, even though the final snapshot is unchanged. Fewer than two observed directory events make the negative control invalid and BLOCKED as well; no fake missing event can be promoted into safe evidence. All four manual negative-control modes remain mutually exclusive.

Seven new tests raise the combined source-defined count to **42**, including a fifth opt-in local Linux OS demonstration that normal GitHub CI deliberately skips. The synthetic tests explicitly cover restored inventory, incomplete/missing event evidence, event decoding and incompatible modes. Even an internally consistent clean case remains only `LOCAL_DISPOSABLE_WITNESS_UNVERIFIED`, not an actual runner security PASS.

This prototype still does not prove that the event collector is trusted, all aliases and namespaces were watched, no queue overflow occurred outside the sampled interval, or that privileged sibling writers were prevented. The real annual runner OS and one-shot admission gates remain BLOCKED.

## DEC-681 — No silent success from a bounded-but-incomplete event drain

The DEC-677–680 collector read at most 16 chunks of 4 KiB and returned whatever had been read. If its limit was reached **while the kernel still reported unread queue data**, an uninspected event (including a future overflow or invalidation) could be omitted without the local report disclosing its incomplete observation. Similarly, poll error/hangup and an unexpected zero-length read after reported readiness were not distinguished from a genuinely quiet watch.

This stacked correction now examines poll error, HUP, NVAL and unexpected descriptor flags, and **raises a fail-closed error** for any of them. An empty read or `BlockingIOError` after readable status also fails. After 16 chunks, the observer performs a final nonblocking readiness check; if the queue is still readable it raises a bounded-drain-incomplete error rather than returning apparently complete data. Missing or incomplete observations remain `BLOCKED`, exit 2, with no annual-runner permission.

Seven additional regressions bring the source-defined count to **49** (five real Linux demonstrations remain manual opt-in). Adversarial tests simulate persistent unread data at the exact 64KiB cap, an exactly drained cap, poll errors and unexpected FD, readable EOF, readiness races, and an ordinary one-chunk drain. This is **input handling hardening**, not a guarantee of kernel event completeness across the entire process lifetime. A quiet instant does not prove future events cannot arrive after watch closure, or that all mount/inode aliases were instrumented.

## Important limitations

**inotify is event observation, NOT OS write prevention.** It does not stop a privileged writer, make a read-only checkout, authenticate the observer process, protect against queue overflow or missed windows between installing/removing watches, cover arbitrary writable inode aliases, handle all mount namespaces or guarantee audit completeness after a malicious process tampers with the collector. It is especially not a substitute for independently enforcing a no-write sandbox. The demonstration uses its own unprivileged process to generate and collect events; the observer is not a separately trusted runner service.

No actual 20-job annual preflight+18 cell+freeze observer evidence, protected data, publisher receipt or authenticated kernel security profile is provided. DEC-650 draft #820 real OS confinement and DEC-651 draft #821 / issue #779 exclusive server-side immutable one-shot dispatch remain BLOCKED. Green synthetic tests do not authorize annual run 385.

**Hard stops:** no merge/ready promotion, actual 385 dispatch/test/rerun/retry, protected annual artifact reads, main/refs/workflow/ruleset/permission/runner changes, broker or trading action.
