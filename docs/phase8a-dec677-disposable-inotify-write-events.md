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

## DEC-682 — Reject structurally complete but semantically unknown event records

Even a bounded, fully drained byte buffer is not reliable evidence if the decoder accepts **a zero action mask** or unknown event flag bits and treats the record as uneventful. This stacked change explicitly enumerates the supported file and directory inotify action flags, allows `IN_ISDIR` only as a modifier of a real event, and rejects records with no known action or unsupported flags. `IN_Q_OVERFLOW` must be the sole mask of an event with the kernel's special watch descriptor `-1`; inconsistent overflow reports fail closed rather than being ignored.

Eight source-defined tests raise the current harness to **57 tests** (five manual Linux OS demos remain opt-in and skipped by default). They cover a zero mask, unknown high flag, unhandled unmount flag, a bare directory marker, valid directory marker plus create, wrong watch number for queue overflow, mixed overflow flags and a known valid close-write event. These are **synthetic parser inputs**, not independently authenticated kernel records; successful parsing can only yield LOCAL_DISPOSABLE_WITNESS_UNVERIFIED, never an annual security PASS.

Requiring known flags makes the parser more conservative but cannot ensure uninterrupted observation, kernel policy enforcement, coverage of every inode alias, completeness across the job lifetime, an untampered observer or actual 20-job runner evidence.

## DEC-683 — Bind event meaning to the right watch descriptor

The DEC-682 parser checks event mask allowlisting and accepts records for either the original **regular-file** watch or its **containing-directory** watch. It did not enforce which category of event belonged to which object. A syntactically valid `IN_CREATE`, `IN_DELETE`, `IN_MOVED_FROM` or `IN_MOVED_TO` record attributed to the *file* watch could therefore be accepted without increasing `write_events` or `directory_changes`, making that malformed observation look clean. Likewise, the `IN_ISDIR` modifier on the known regular-file watch was not rejected.

The new decoder rejects all directory-entry masks or `IN_ISDIR` on the regular-file watch, and fails closed if the claimed directory-watch identity is not a nonnegative strict integer **distinct from the file-watch ID**. A real directory create event on the directory watch and a valid file close-write event remain separately counted, preserving intended Linux behavior.

Seven new source-defined regressions raise the suite to **64 cases**, with five manually opt-in local Linux demonstrations still skipped during ordinary CI. The tests cover all directory-entry event types misattributed to the file, unexpected directory modifier, a single-file-watch spoof, aliased watch IDs, malformed watch ID values, legitimate dual-watch events and normal file write events. These check parser consistency only; actual watcher registration and source integrity require independent proof on the restricted runner.

## DEC-684 — Bound event filename layout to the watch type

The earlier inotify decoder bounded the `len` field but did not validate its contents. A directory `IN_CREATE` record with **no filename**, an un-terminated filename, embedded invalid path separators or nonzero trailing padding could therefore appear structurally well formed. A regular-file watch event could also carry a fabricated filename. This is distinct from DEC-683's mask/watch-ID provenance requirement.

The parser now requires `len=0` for the known regular-file watch and the special overflow event. For a directory-watch child-entry mutation, a **nonempty, single-basename**, NUL-terminated filename is mandatory. DEC-684 originally required 4-byte alignment (corrected to native 16-byte alignment in DEC-696 below), with only zero bytes following the first NUL; slash-containing path strings are rejected. A directory watcher can still receive name-free self events that do not report child directory-entry mutations. The existing synthetic `ev()` helper was updated to produce realistic named and zero-padded directory child events.

Nine new source-defined tests bring the suite to **73 tests** (five manual Linux demonstrations stay optional/skipped in routine CI). Cases cover missing filename, no terminator, nonzero padding, empty name, path separators, a named file-watch record, unaligned name length, correct padding and a named overflow record. Malformed layout yields `BLOCKED`, never zero exit or real authority.

This is a conservative offline parser consistency check, **not trusted kernel telemetry** or proof of actual OS-enforced write prevention. Runtime inode aliases, privileged host siblings and the 20 real protected annual jobs remain outside this toy observer.

## DEC-685 — Reject short or changed source-file snapshot reads

Even a no-following, bounded regular-file descriptor does not automatically guarantee an **internally consistent** observation when another writer can modify the inode during the read. The predecessor checked initial size at most 4 KiB, then accepted whatever number of bytes `os.read` returned. A short read, growth/shrink or changed inode metadata could appear as if it were the complete expected source.

The new helper reads at most the validated original size plus one byte and requires **exactly the originally observed size**. It then takes a second `fstat` and compares device, inode, size, modification time and change time against the first `fstat`. A mismatched length or metadata produces an explicit fail-stop `OSError`, causing `BLOCKED` rather than a clean observation. The code does not follow a symlink, block on a FIFO or open any real annual source path.

Six added tests increase the synthetic suite to **79 source-defined cases**. They inject a short `read`, concurrent append, same-length content rewrite, metadata change and oversized rejection, plus an empty-file bounded control. These tests run only against generated public temporary files.

**Limitation:** `fstat` before and after a read is another point-in-time measurement. An adversary able to write, restore bytes and manipulate metadata could evade it; even honest filesystems may not offer forensic causality guarantees from nanosecond timestamps. The actual runner still needs OS-enforced prevention and independently authenticated evidence, not a snapshot heuristic.

## DEC-686 — Complete two-watch coverage is mandatory for a clean toy outcome

Since DEC-679, the disposable observer's threat model depends on **both** a watch on the original regular-file inode and a separate watch on the containing fake checkout directory. The parser could inspect a file-only stream without its optional directory-watch ID and report structural consistency; the evaluator could then return LOCAL_DISPOSABLE_WITNESS_UNVERIFIED for a quiet file-only observation. That **understates the coverage actually required** to assess directory-entry changes.

The evaluator now requires strict integer, nonnegative and *distinct* file and directory watch IDs as an additional observed property, `both_watches_identified`. Missing, aliased or malformed watch identifiers make the overall result `BLOCKED`, even if event bytes, inode identity and final inventory happen to look unchanged. A quiet synthetic two-watch result remains only LOCAL_DISPOSABLE_WITNESS_UNVERIFIED, exit 3, never annual authorization.

Five additional regression cases bring this stacked suite to **84 source-defined tests**, with five manually opt-in real Linux scenarios still skipped by normal CI. Tests distinguish missing file-only coverage, valid two-watch toy completeness, aliased watch identities, wrong type/negative file IDs and invalid directory watch IDs. The existing synthetic clean test was updated to supply the legitimate separate directory-watch ID.

**Limit:** two integer labels in an untrusted test are not proof that kernel watches were actually installed and retained for the lifetime of an annual job. Only independent OS and observer attestation can establish real coverage. The source remains nonauthorizing and out of production.

## DEC-687 — Bound claimed watch identities to Linux signed 32-bit descriptors

The DEC-686 dual-watch presence test required strict nonnegative Python integers and distinct file/directory IDs, but accepted arbitrarily large integers. Linux inotify watch descriptors are returned as **signed 32-bit** values by `inotify_add_watch`. A caller could therefore pass two impossible positive numbers with an empty synthetic event stream and obtain `LOCAL_DISPOSABLE_WITNESS_UNVERIFIED`, falsely implying even the internal watch-identity structure was plausible.

Both the byte-stream decoder and evaluator now require each watch ID to lie in the inclusive signed nonnegative range `0..2^31-1` and remain distinct. Four new source-defined tests raise the suite to **88 cases**: impossible file-watch IDs, impossible directory-watch IDs, the inclusive maximum boundary, and an oversized directory watch alongside a legitimate file event. These are parser-consistency checks on invented public event records, not kernel provenance claims. The status remains `BLOCKED` or `LOCAL_DISPOSABLE_WITNESS_UNVERIFIED`, never authorization. Exact-head Phase 3/full regression and independent review remain required.

## DEC-688 — A transient sibling must have a matching create/delete event pair

The earlier transient-directory negative check equated **two directory-change records** with evidence of a create-then-delete control. Two `IN_CREATE` records, two `IN_DELETE` records, or a create for one leaf followed by a delete for another could satisfy `transient_directory_control_detected`. The final outcome was still `BLOCKED`, but the claimed negative-control detection was not supported by its events.

The parser now tracks validated directory-watch child names: an `IN_CREATE` must precede an `IN_DELETE` of the **same basename** to count as a `transient_create_delete_pairs` witness. The evaluator uses at least one matched pair for the deliberate transient negative mode, instead of simply counting events. Six new synthetic regressions bring the suite to **94 source-defined tests**: duplicate creates, duplicate deletes, mismatched names, reversed order, interleaved matching events and a combined-action spoof. The real Linux demonstration still creates and unlinks one disposable sibling after watch installation.

This is **not authenticated or complete kernel evidence**; it merely stops the harness from overstating its own negative-control observation. All modes remain nonauthorizing, and exact-head CI plus independent review are still needed.

## DEC-689 — Source-write negative control requires source-file content events

The earlier write/revert negative check used `write_events >= 2`, a conservative counter of **both file and directory watch** modification/attribute records. Two metadata notifications on the directory watch, or two `IN_ATTRIB` notifications on the watched file, could mark `negative_control_detected=true` without observing any write to the original source file's content. The overall verdict remained `BLOCKED`, but the negative-control detection claim was too broad.

The decoder keeps `write_events` conservative for fail-closed blocking, while separately counting `source_content_write_events`: only `IN_MODIFY` or `IN_CLOSE_WRITE` attributed to the original *file watch*. The deliberate write/revert control now requires **two source-content event records**, a well-formed, non-overflowed, non-invalidated event stream and a confirmed live collector flag. Four added synthetic tests raise the suite to **98 source-defined cases**: two directory-only writes, two file metadata-only events, one source plus one directory write, and a valid two-event source-content control.

This stronger self-check still cannot authenticate the kernel record origin or establish prevention, continuity, or annual runner confinement. Exact-head CI and independent review required; no authorization change.

## DEC-690 — Require exact inotify poll readability, not arbitrary poll activity

The bounded collector previously treated any nonempty `poll()` response as readable unless it included an explicit error/HUP/NVAL bit or an unknown FD. A record containing `POLLPRI`, unknown bits, or even **zero readiness flags** could trigger an `os.read` and appear to satisfy collection if an injected read returned event bytes. That is not evidence that the registered inotify queue reported normal readable status.

The collector now accepts either an **empty** readiness result (quiet) or **one exact** `(registered_fd, POLLIN)` record. Other masks, unexpected IDs or duplicate records raise a fail-closed `OSError` before attempting to read. Three new source-defined regression methods raise the suite to **101 cases**: invalid/zero/unknown flags (multiple subcases), duplicate poll entries, and a valid `POLLIN` control. Existing EOF, overflow, bounded-drain and poll error/HUP/NVAL tests still apply.

This does not establish continuous completeness or trustworthy kernel-originated evidence, only internally conservative handling of the observer's readiness input. Exact-head CI and independent review remain required.

## DEC-691 — Reject rename-cookie contamination in non-move inotify events

The previous decoder ignored the 32-bit `inotify_event.cookie` field. Linux associates that field with directory move/rename events; non-move events do not gain a nonzero rename cookie. Consequently, a synthetic `IN_MODIFY`, `IN_CLOSE_WRITE`, `IN_ATTRIB`, `IN_CREATE` or `IN_DELETE` could carry a fabricated nonzero move cookie and still be treated as structurally normal.

Nonzero cookies are now rejected **unless** the event includes `IN_MOVED_FROM` or `IN_MOVED_TO`. We do not claim to authenticate or correlate move pairs; any directory move remains a blocked mutation. Four new source-defined tests raise the suite to **105 methods**: file non-move spoof, directory non-move spoof, valid paired-looking move-cookie records (still BLOCKED) and a zero-cookie file-event control. Ordinary inotify demonstrations remain manual and cannot authorize the annual workflow.

This checks one field's meaning, not actual kernel-origin authenticity or OS isolation. Exact-head CI and independent review are still needed.

## DEC-692 — Reject multiple primary action bits in one event record

The parser already rejected an actionless event or unknown flags, but accepted a single synthetic record combining two unrelated primary actions (e.g. `IN_MODIFY | IN_CLOSE_WRITE` or `IN_CREATE | IN_DELETE`). Such fabricated combinations could be interpreted as internally well-formed even though the inotify API emits one primary event action per record. In particular, a mixed source-file mask should not be mistaken for one authentic content event.

The decoder now requires **exactly one** supported primary action bit. `IN_ISDIR` remains an allowed modifier on the directory watch, and ordinary individual `IN_MODIFY`, `IN_CLOSE_WRITE`, `IN_CREATE` and `IN_DELETE` records remain supported in their appropriate watch scope. Four new source-defined tests raise the suite to **109 cases**, checking multi-action file records, multi-action directory records, valid `IN_ISDIR` directory create and two valid separate source writes.

This deliberately conservative decoder change does not establish kernel authenticity, job-wide visibility or OS write prevention. Exact-head GitHub CI and independent review required.

## DEC-693 — Reject impossible dot-directory entry names

The decoder already rejected empty or slash-containing child basenames but still accepted `.` and `..` as named directory-entry mutations. These are special directory navigation components, not new removable children that Linux `IN_CREATE`/`IN_DELETE` can legitimately report. The matching-pair negative witness could therefore count a fabricated create/delete pair for `.` as detected.

The parser now rejects exact `b"."` and `b".."` in named directory-watch events. Three source-defined regressions raise the suite to **112 tests**, covering both impossible single create names, forged matching transient pairs, and valid dot-prefixed actual names like `.env`. All suspicious/invalid events still BLOCK; real Linux samples and repository isolation remain out of scope.

This is another bounded synthetic-decoder consistency check, not kernel provenance or write-prevention evidence; exact-head CI and independent review remain required.

## DEC-694 — Enforce poll return type and single-read maximum

After restricting the readiness mask in DEC-690, the collector could still interpret `select.poll.poll()` returning a false-like **non-list** (`None`, tuple or map) as a legitimately quiet event queue. Those are not valid Python `select.poll.poll()` results. Likewise, the collector previously trusted the shape of a patched `os.read(fd, 4096)` response: an impossible **4097-byte** return could be appended if the aggregate remained below 64 KiB, and non-byte returns could produce uncontrolled `TypeError` rather than a reported `BLOCKED` result.

The collector now insists on an actual readiness *list* and a `bytes` chunk with length at most 4096 on each readable pass. Other values raise a handled `OSError`; actual EOF and empty-queue race errors retain their existing fail-closed results. Three new synthetic fault-test methods bring the test suite to **115 source-defined cases**, exercising malformed quietness, oversized chunks and non-byte chunks. The collector's kernel demonstrated cases remain manual opt-in.

As elsewhere, this validates local collector assumptions only; neither injected/mock safety nor a quiet poll establishes complete trusted host observation. Exact-head CI and independent security review required.

## DEC-695 — Negative control detection requires a complete, live event stream

After DEC-688 required matching create/delete names, the synthetic evaluator still set `transient_directory_control_detected=true` when it saw a matching pair even if the **same stream was truncated, overflowed, invalidated or had no live collector**. Such a stream was always `BLOCKED`, but the negative-control detection field overstated the reliability of the witness. DEC-689's source-write negative already demanded an intact event stream; the transient-directory control did not.

The transient control now requires `well_formed`, **no** queue overflow, **no** watch invalidation, strict live-watcher truth and at least one matching child create/delete pair. The dedicated missing-negative finding is tied to that complete predicate as well. Four synthetic fault-injection tests bring the suite to **119 source-defined cases**: malformed trailing event, queue overflow, removed watch and dead collector after an otherwise valid pair. The existing valid pair stays detected but **BLOCKED** and never authorizes an annual runner.

This is evidence-accounting consistency for the disposable observer, not a claim of complete trusted kernel monitoring or OS confinement. Exact-head CI and independent source/security review remain required.

## DEC-696 — Validate Linux's native 16-byte inotify name padding

DEC-684 used `len % 4 == 0` for the event name field and wrote matching synthetic fixtures. Linux's `fs/notify/inotify/inotify_user.c` instead calculates **`roundup(name_len + 1, sizeof(struct inotify_event))`**, with a 16-byte inotify event header. Four-, eight- and twelve-byte child-name payloads were therefore incorrectly accepted as plausible kernel records.

The parser now uses `nbytes % EVENT.size == 0`. The synthetic fixture supplies native 16-byte-padding, including directory changes, matched transient create/delete records, dot-prefixed names, impossible-name negatives, and named overflow spoofs. Four new tests increase the source-defined suite to **123**: bad 4/8/12 padding, valid 16-byte minimum, valid 32-byte padded long name and named directory metadata alignment.

The real Linux source files and `inotify(7)` justify this structural correction, but no kernel event is independently authenticated and this does not establish actual OS write prevention or annual-runner proof. Exact-head Phase 3/full CI and qualified independent review remain required.

## DEC-697 — Require the exact minimal Linux name-field roundup

DEC-696 corrected 4-byte padding to a multiple of the 16-byte inotify event header, but still accepted **arbitrarily extra zero padding**. For example, a one-character basename with a 32-byte name field passed the decoder even though Linux `round_event_name_len` emits the **minimum** `roundup(name_len+1, sizeof(struct inotify_event))` size: 16 bytes for that basename.

The decoder now requires `nbytes == ((terminator + EVENT.size) // EVENT.size) * EVENT.size`, after validating the terminating NUL. Four new source-defined tests raise the suite to **127 tests**: reject an over-padded one-byte basename, reject a 15-byte name with 48 bytes of padding, preserve exact 15-byte/16-byte basename boundaries, and reject excessive padding on named directory metadata events. Existing negative controls and opt-in live Linux demonstrations remain nonauthorizing.

The Linux kernel source confirms the exact packing rule. This is a source-grounded structural consistency repair, not an authenticated OS audit or annual run385 permission. Exact-head CI and independent security review remain required.

## DEC-698 — Bound directory child basename to Linux NAME_MAX

After enforcing native minimal 16-byte padding in DEC-696/697, the decoder still accepted a structurally padded `IN_CREATE` for a filename of **256 bytes or more**. Linux's UAPI `include/uapi/linux/limits.h` defines `NAME_MAX = 255` bytes for a single filename component, and `inotify(7)` describes the emitted `name` as a child basename rather than a full path.

The parser now caps the basename at 255 non-NUL bytes while retaining exact kernel name-field rounding. Three tests bring the suite to **130 source-defined methods**: 255-byte name boundary structurally accepted, 256-byte name rejected, and a 300-byte name cannot forge matched transient negative-control detection. This remains confined to the disposable /tmp observer, not a trusted OS evidence collector, and exact-head CI plus independent source/security review are still required.

## DEC-699 — Bounded deterministic adversarial event corpus

Earlier DEC-677–698 regressions individually exercised malformed fields, watch identities and event layout. A reproducible broader corpus now probes combinations without using real annual data or arbitrary operating-system paths.

Three source-only test methods add **512 pseudo-random byte buffers**, **512 independently synthesized forged inotify headers** and bounded bit flips across two legitimate-looking event records. Seeds are fixed and data sizes bounded, so CI is deterministic and cheap. The tests insist that the parser doesn't throw on hostile bytes and that every evaluated outcome preserves `can_authorize_dispatch=false`, `independent_os_proof_verified=false`; forged event headers are always `BLOCKED`. This raises the source-defined suite to **133 test methods**, while leaving production code untouched.

The corpus cannot prove exhaustive coverage, authenticated kernel records, continuous observation, OS write prevention or annual authorization. Five real Linux demonstrations remain manual opt-in; independent reviewer assessment and exact-head Phase 3/full CI are required.

## DEC-700 — Match the transient *file* witness, not a directory pair

The DEC-688 transient control matches a child `IN_CREATE` followed by `IN_DELETE` with the same basename. The actual opt-in control creates a **regular file**, but the matcher ignored `IN_ISDIR`. Two events for a short-lived *directory* could therefore set `transient_directory_control_detected=true`, even though the deliberate file control had not been witnessed. The overall negative result was already `BLOCKED`; its evidence-accounting field was too permissive.

The matcher now tracks only creates without `IN_ISDIR` and credits a matched delete only when that delete also lacks `IN_ISDIR`. A directory create/delete with the same name clears a stale pending file creation rather than legitimizing it. Directory entry changes of either type still independently **BLOCK** the main evaluation. Five additional source-defined tests bring the suite to **138 methods**: directory-only pair, mixed-type pairs in both directions, directory recreation invalidating pending file evidence, and a legitimate file pair. Five manually opt-in real Linux demonstrations remain unchanged.

No kernel provenance or read-only OS enforcement follows. Phase 3/full CI at the exact head and independent source/security review remain required.

## DEC-701 — Write-open closes are not proof of two modified contents

The DEC-689 file-watch provenance fix still counted both `IN_MODIFY` and `IN_CLOSE_WRITE` in `source_content_write_events` for the deliberate write/revert control. Linux `inotify(7)` defines `IN_CLOSE_WRITE` as the **closing of a file opened for writing**, which does not itself prove a write occurred. Two close notifications, or a single modify followed by close, could thus make `negative_control_detected=true` without observations of two distinct source modifications. Overall status was already `BLOCKED` but the positive negative-control finding overstated its evidence.

A separate `source_modify_events` counter now requires at least **two `IN_MODIFY` notifications from the original regular-file watch** for this specific negative-control claim, along with the existing intact/live stream gate. The conservative `write_events` and `source_content_write_events` remain unchanged to block any suspicious file or directory activity. Four new regression methods bring the synthetic suite to **142 cases**: two close-write-only events, one modify + close, two modifies with an interleaved close, and directory-only modifies. Existing positive fixture assertions now use actual modify records.

This is still only untrusted event metadata; a modify notification does not prove specific intermediate file contents, absence of aliases, independent provenance or OS write prevention. The live Linux opt-in demonstrations still need external verification, exact-head CI and qualified security review.

## DEC-702 — Bound and type-check simulated before/after source snapshots

The `_snapshot_regular` helper reads an at-most-4096-byte regular synthetic inode, but the independent evaluator `_evaluate` unconditionally invoked `hashlib.sha256(before)` and `hashlib.sha256(after)` before checking whether callers supplied actual bounded `bytes`. A malformed injected `str`, `None`, list or boolean snapshot could raise `TypeError` instead of returning the intended `BLOCKED` JSON receipt. An oversized direct-input snapshot also exceeded the helper's documented 4 KiB domain.

The evaluator now rejects wrong-type snapshots or snapshot lengths above 4096 bytes immediately with an explicitly nonauthorizing `BLOCKED` outcome. Three synthetic unit methods bring the suite to **145 cases**, covering malformed value types, oversized initial/final snapshots, and an exact-limit clean-but-unverified control. `run_demo` still uses only freshly generated public files and the preexisting bounded FD snapshot.

This protects the narrow harness API, not all callers/filesystems or real annual runner source integrity. Exact-head CI and independent review remain required.

## DEC-703 — Persistent sibling witness must name the expected regular file

The DEC-679 persistent-sibling negative creates the exact regular filename `unexpected-public-sibling` inside the disposable directory and leaves it present at final inventory. Its later evaluator only asked whether **any** directory mutation was observed or the final inventory was dirty. An unrelated filename or a directory creation could therefore make the control look detected, even if the expected file was never observed. Overall status was already `BLOCKED`, but the affirmative negative-control evidence was too weak.

The decoder now records whether a valid directory-watch `IN_CREATE` (without `IN_ISDIR`) named the **expected regular sibling**. The dedicated `sibling_creation_control_detected` check also requires an intact/live stream and final inventory *not* equal to the original single-file inventory. A directory or unrelated child cannot spoof the negative observation. Five regression methods raise the suite to **150 source-defined cases**, including unrelated child creation, correct expected filename, directory-kind spoof, clean final inventory despite claimed creation, and queue overflow after an otherwise correct event.

This remains a self-generated untrusted `/tmp` observation. A dirty inventory boolean is not independently authenticated evidence of a specific surviving file, and no OS prevention or annual run authorization follows. Exact-head CI and independent security review remain required.

## DEC-704 — Bind persistent sibling negative to its exact final filename inventory

DEC-703 required the correct `IN_CREATE` filename and a dirty final directory inventory, but `directory_inventory_ok=False` only means the final inventory differs from `["sample"]`. A different extra leaf could keep that boolean false after the expected sibling was deleted, while the earlier expected `IN_CREATE` event still made the persistent-file negative appear detected.

The observer now collects the actual **sorted tuple of generated filenames**, and the persistent-sibling control only counts when it equals exactly `("sample", "unexpected-public-sibling")` and the expected regular-file `IN_CREATE` was recorded on an intact live directory watch. The evaluator's new optional `directory_inventory_names` argument is used only for that specific control; missing, list-typed, reordered or mismatched names cannot satisfy the predicate. Three added unit methods raise the suite to **153 source-defined tests**, distinguishing wrong final leaf, malformed/missing inventory, and an expected inventory without the expected event. The existing positive unit fixture is updated to supply the exact expected names.

Both the generated fixture name and the decoder share one constant. This only prevents the synthetic evaluator from overstating **its own local negative-control witness**; no independent protected runner source provenance, hostile mount namespace coverage or actual write prevention is established. Exact-head CI and qualified independent security review remain necessary.

## DEC-705 — Persistent sibling final entry must still be the pinned regular inode

DEC-704 checks exact final filename inventory and the named `IN_CREATE` record, but filenames alone do not prove the surviving `unexpected-public-sibling` path still references the **same regular file** the negative control created. An actor could replace that pathname with a symlink or different inode, or rewrite its bytes, while retaining the expected directory entry names.

The disposable demo now records the synthetic sibling's initial regular-file `(st_dev, st_ino)` and exact `PUBLIC-EXTRA` bytes using the existing bounded `O_NOFOLLOW` snapshot helper. After draining events, it takes another bounded/no-follow sibling snapshot. Its dedicated control only counts when the same inode and bytes remain, in addition to the exact final inventory and directory-watch creation event. A missing or symlink-substituted sibling causes a fail-closed `BLOCKED` outcome. The evaluator uses a strict `sibling_snapshot_stable is True` flag for synthetic fault tests.

Three added source-defined regression methods bring the suite to **156 cases**: malformed/false stability claims, a symlink substitution refusal, and same-inode rewritten bytes. This is two point-in-time observations on a generated `/tmp` fixture, not continuous source immutability, mount-alias exclusion, authenticated host evidence or actual OS-enforced prevention. Exact-head CI and qualified independent security review remain required.

## DEC-706 — Restore syntactic validity of early fail-closed decoder returns

An audit of exact-head full historical GitHub CI found that #874–876 **failed**, despite passing Phase 3. The failing test-module import identified a `SyntaxError` in `scripts/dec677_disposable_inotify_events.py` around the start of `_classify_stream`. DEC-701 expanded the decoder's early-return dictionaries with a new counter and inadvertently removed their closing `}` characters; DEC-703 later added another field to those same lines without restoring the missing braces. All three defensive return branches had malformed Python source, so unit tests were never imported.

This child patch restores the **three closing braces only** in the observer source; it also adds two synthetic methods exercising malformed buffer, watch identity, directory identity and blocked evaluation returns. The source-defined suite increases to **158 tests**. The historical failing #874–876 heads remain unchanged and **must not be relabeled green**; exact-head Phase 3 and full CI are required independently for this fix.

No annual workflow, protected inputs, real runner controls or authoritative dispatch settings were modified.

## DEC-707 — Match the actual sorted sibling directory inventory

The DEC-704/705 persistent-sibling control collects `tuple(sorted(p.name for p in Path(folder).iterdir()))`, but compared it against `("sample", "unexpected-public-sibling")`. Python sorts `"unexpected-public-sibling"` **before** `"sample"`, so the actual correct generated directory could **never** satisfy that constant, even with an intact event stream and the correct sibling inode. Historical positive synthetic fixtures had copied the wrong tuple and concealed the mismatch.

The comparison now uses `tuple(sorted(("sample", PERSISTENT_SIBLING_NAME)))`, and the positive fixture uses the true order `("unexpected-public-sibling", "sample")`. The old supposedly-reordered negative is inverted. Two new source-defined tests raise the suite to **160**: a temporary generated directory's *actual sorted enumeration* must satisfy the local persistent-sibling control and an incorrectly ordered direct tuple must not. They do not execute annual runners or their protected data.

This is the second post-#876 consistency repair, stacked on DEC-706 syntax restoration, not proof of independently trusted Linux event coverage or enforced source immutability. Exact-head CI and qualified source/security review are required.

## DEC-708 — Verify the *intermediate* disposable write/revert snapshot

The write/revert negative had a meaningful evidence gap even after DEC-701 required two file-watch `IN_MODIFY` records: its final bytes and digest matched the initial contents, but there was **no point-in-time snapshot** proving this generated sample had reached the intended `AFTER` bytes between writes. Two modifications followed by a final `BEFORE` digest cannot alone attribute the intermediate payload or the deliberate revert.

In the **public, self-generated `/tmp` fixture only**, the demo now takes a bounded, no-follow `_snapshot_regular` immediately after writing/fsyncing `AFTER`, verifies the original inode and exact changed bytes, then writes/fsyncs `BEFORE`. The evaluator's `midpoint_source_snapshot_matches_expected` check requires strict `True`, and the negative-control detection also requires this condition in addition to the existing two source `IN_MODIFY` records, intact/live event stream and ordinary overall BLOCKED outcome.

Four added synthetic tests raise the suite to **164 source-defined methods**: missing/wrong-type/false midpoint evidence, valid intermediate evidence plus two modifies, midpoint evidence with close-write-only events, and malformed event stream after two modifies. Three earlier synthetic positive cases explicitly supply the local midpoint flag. The five optional real Linux demos remain untrusted and manual.

Two self-generated point-in-time snapshots plus notification metadata are **not** continuous OS immutability, a kernel-authenticated audit, intermediate-proof cryptographic attestation, or annual-runner authority. Exact-head CI and qualified independent review are mandatory.

## Important limitations

**inotify is event observation, NOT OS write prevention.** It does not stop a privileged writer, make a read-only checkout, authenticate the observer process, protect against queue overflow or missed windows between installing/removing watches, cover arbitrary writable inode aliases, handle all mount namespaces or guarantee audit completeness after a malicious process tampers with the collector. It is especially not a substitute for independently enforcing a no-write sandbox. The demonstration uses its own unprivileged process to generate and collect events; the observer is not a separately trusted runner service.

No actual 20-job annual preflight+18 cell+freeze observer evidence, protected data, publisher receipt or authenticated kernel security profile is provided. DEC-650 draft #820 real OS confinement and DEC-651 draft #821 / issue #779 exclusive server-side immutable one-shot dispatch remain BLOCKED. Green synthetic tests do not authorize annual run 385.

**Hard stops:** no merge/ready promotion, actual 385 dispatch/test/rerun/retry, protected annual artifact reads, main/refs/workflow/ruleset/permission/runner changes, broker or trading action.
