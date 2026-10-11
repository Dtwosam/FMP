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

## DEC-709 — Install both watches before taking the baseline snapshot

The disposable demo previously opened and read its original `sample` inode **before** calling `_start_watch`. A file rewrite between that initial read and the actual Linux inotify watch registrations could escape the event log, even though a later before/after digest might match. The fresh `/tmp` fixture's permissions limit the practical exposure but do not justify presenting an unobserved baseline window as part of complete event capture.

The demo now installs both file and parent-directory watches first, then obtains the initial bounded regular-file snapshot **inside the watch FD's `try/finally` cleanup scope**. An initial snapshot failure now closes the installed inotify FD and fails closed. Two synthetic, POSIX-safe but Linux-gated regression methods increase the suite to **166**: assert the registration precedes the initial source snapshot and assert FD cleanup when that snapshot fails. This does not change any real annual workflow, protected source file or permission setting.

It narrows one self-observation window but does not prove continuous external kernel-event provenance or close the inherent gap after a final queue drain; DEC-650 actual OS isolation and independent qualified review remain required.

## DEC-710 — Drain events after final source and directory observations

The demo previously called `_read_pending(fd)` **before** reading its final source inode, enumerating child filenames and optionally checking the surviving sibling inode. A write or directory mutation occurring during these later observations could miss the collected event stream while all end-state checks appeared internally consistent. This is a real sampling-order gap in the self-generated observer; inotify does not prevent the write.

The observer now completes all final bounded/no-follow source and optional sibling snapshots and the directory inventory **before** its bounded event-queue drain. It then evaluates the drained events against the end-state evidence, while the same inotify FD stays installed until cleanup. Two new Linux-gated mocked-order regressions raise the suite to **168 source-defined tests**, verifying that final snapshot precedes the drain and that an injected modification during that snapshot is reported as `BLOCKED`.

This shrinks only the **in-process sample interval**. It cannot guarantee no write after the final drain, that no pending records appear outside the polling window, that an adversarial process could not tamper with the observer, or that OS-backed write denial exists. Exact-head CI and independent qualified OS security review remain required.

## DEC-711 — Match the transient negative to its exact generated basename

The transient write/remove mode creates a regular child named `temporary-public-sibling`. DEC-688 and DEC-700 required same-basename ordered creation/deletion with no `IN_ISDIR`, but accepted **any** transient regular-file pair as detection of this specific negative control. A completely unrelated create/delete pair could therefore claim `transient_directory_control_detected=true` even though the deliberate filename was not witnessed; the overall result still BLOCKED.

The decoder retains the general `transient_create_delete_pairs` counter and adds an `expected_transient_pairs` count for the exact generated regular child. Only that latter counter qualifies the negative-control predicate alongside the existing live, well-formed, nonoverflowed and noninvalidated stream conditions. The actual generator and parser share one constant. Three older synthetic positive cases now use the true expected name.

Five focused source-defined tests bring the suite to **173 methods**: reject unrelated pairs, detect the known regular child (still BLOCKED), reject same-name directory pairs, reject mismatched create/delete basenames and reject valid expected pair followed by queue overflow. The five manual opt-in Linux disposable demonstrations remain separate.

The tighter toy basename attribution is not independent kernel-origin proof, actual write prevention or annual run385 authorization. Exact-head Phase 3/full CI and independent qualified review remain necessary.

## DEC-712 — Transient negative requires the expected clean final inventory

DEC-711 tied the transient-create/delete pair to the exact generated basename. However, the negative control still claimed detection when an expected create/delete pair appeared **even if another unexpected directory entry survived** or final directory enumeration was missing. A deliberate transient sibling should leave the directory with exactly the original `sample` entry after the expected create/delete events.

The `transient_directory_control_detected` check now also demands strict `directory_inventory_ok is True` and a strictly typed `directory_inventory_names == ("sample",)` tuple. An unrelated surviving child, an untrusted list, missing names or a false inventory flag defeats the local detection claim, while the overall deliberate negative always BLOCKS. Four source-defined regressions bring the suite to **177 methods**; four existing positive synthetic fixtures are updated to supply the expected final inventory, matching the real demo's enumeration.

This only checks self-generated /tmp filenames against expected event counts. It is not continuous host-wide directory immutability or proof that no protected checkout contents changed. Exact-head CI and independent qualified security review remain required.

## DEC-713 — A quiet stream is not a clean directory without named inventory

The general `no_directory_entry_mutations` check still credited a quiet event buffer and caller-supplied `directory_inventory_ok=True`, **even if the exact final filenames were absent, differently typed, or inconsistent with the synthetic original**. DEC-704 and DEC-712 already required exact filenames for their two specific negative controls; the default local-clean observation remained weaker.

The general check now requires **zero directory mutation events**, strictly true inventory flag and an exact tuple `directory_inventory_names == ("sample",)`. Unknown or false-typed names cannot claim a clean generated directory; actual `run_demo` already enumerates and passes that sorted tuple. Four older synthetic clean controls are updated to supply the same positive evidence as the demo. Three added tests bring the suite to **180 source-defined methods**, covering missing final filenames, wrong type/wrong names, and exact single original filename with a nonauthorizing local-unverified result.

This remains only the integrity of the observer's self-generated fixtures. Source-tree immutability, trustworthy externally controlled evidence and actual OS write prohibition are not established. Exact-head CI and independent qualified security review are required.

## DEC-714 — Correct the DEC-707 filename-sort regression (historical red CI)

The historical exact-head full regressions **#878–884 FAILED** although Phase 3 completed green. Source inspection and the actual CI trace established one shared cause: DEC-707 **incorrectly claimed** Python sorts `"unexpected-public-sibling"` before `"sample"`. Python in fact sorts `"sample"` first (`'s' < 'u'`). The DEC-707 assertion, its malformed-inventory inverse test and synthetic positive fixture reversed a previously correct DEC-704 ordering. Three named tests consequently failed in full regression, while the implementation's dynamic `tuple(sorted(...))` comparison already produced the correct order.

DEC-714 restores the three incorrect fixtures to **`("sample", "unexpected-public-sibling")`**, and leaves the dynamic sorted implementation unchanged. An extra regression method explicitly cross-checks Python's actual lexical order with a valid expected sibling witness (still `BLOCKED`). The suite is now **181 source-defined methods**. **DEC-707's explanatory paragraph above is historically inaccurate and is superseded by this finding**; failing parent CI results must remain recorded and must not be relabeled green. Only a new exact-head full successful test run can validate the repair.

This fixes one synthetic test contract mismatch, not authenticated kernel observations or annual runner isolation; DEC-650/651 remain BLOCKED.

## DEC-715 — Cancel a pending transient-file witness on same-name moves

The disposable parser tracks a per-name `IN_CREATE` followed by `IN_DELETE` to recognize the transient public sibling control. An intervening `IN_MOVED_FROM` or `IN_MOVED_TO` for the **same basename** makes that historical create's inode identity ambiguous: the created file may have left the directory, or a replacement with that name may have arrived before the observed delete. The earlier matcher did not invalidate the pending basename, potentially claiming the deliberate create/unlink witness even though those two records might reference different inodes. Every such mutation already BLOCKED, but the `transient_directory_control_detected` evidence claim could be overstated.

DEC-715 clears a pending create whenever `IN_MOVED_FROM` or `IN_MOVED_TO` affects the same named directory entry. A new ordinary regular-file `IN_CREATE` is required before a later matching `IN_DELETE` can count. Four new source-defined unit tests bring the suite to **185 methods**: same-name move-out and move-in invalidate pending evidence, unrelated name moves do not invalidate a valid target pair, and a new create following the same-name move can form a new pair. All deliberate negative cases still BLOCK. This refinement only tightens the local observer's event-correlation claims and does not establish kernel provenance, prevent renames, or substitute for actual annual-runner OS isolation.

## DEC-716 — Snapshot the transient generated file before unlinking it

DEC-712/715 improved matching of the exact transient sibling's `IN_CREATE` and `IN_DELETE` record under the final clean generated directory inventory, but matching event names alone does not demonstrate that the opt-in control actually held the intended **regular file with known public content** between creation and removal. The synthetic evaluator could claim the negative witness without any intermediate file snapshot.

The disposable demo now uses the existing 4KiB bounded, no-follow `_snapshot_regular` helper on `temporary-public-sibling` immediately after it writes exact `PUBLIC-TEMPORARY` and before unlinking it. The evaluation's `transient_midpoint_regular_file_verified` property requires strict `transient_midpoint_verified is True`, and the overall `transient_directory_control_detected` also needs that flag, the complete/living event stream, expected name pair and clean final filename tuple. Six existing positive synthetic tests are updated to supply explicitly known midpoint evidence; negatives remain fail-closed.

Three new source-defined regressions bring the suite to **188 methods**: matching event pair without trusted midpoint, known midpoint but wrong event pair, and an actual generated/no-follow regular-file snapshot followed by deletion (on hosts with `O_NOFOLLOW`). These remain self-generated public point-in-time observations, **not** independent kernel provenance, continuous immutable source or annual OS-confinement proof. Exact-head CI and qualified review remain required.

## DEC-717 — A write/revert negative requires original final bytes and inode

DEC-708 added an intermediate exact public changed-source snapshot; DEC-701 required two original source-file `IN_MODIFY` records. But `negative_control_detected` still did not require the *final* bytes or watched inode identity to equal their baseline. If a direct synthetic evaluator input had valid midpoint evidence and events but ended with altered bytes (not reverted) or a replaced inode containing identical bytes, the dedicated **write/revert** negative could be claimed as detected. The main outcome was already BLOCKED; only its evidence accounting was overstated.

The specific negative-control predicate now also requires strict `before == after` and `inode_stable is True`, matching the existing separate `final_digest_equal` and `watched_inode_matches_final_path` checks. Three new source-defined methods bring the suite to **191**: unrestored final bytes defeat the control claim, a replaced inode with matching bytes defeats it, and unchanged final bytes/inode with two true source `IN_MODIFY` records and a known midpoint preserve a **BLOCKED** positive negative-control observation. These checks remain merely point-in-time public sample evidence, not cryptographic proof of absence of other writers, authenticated inotify, or real annual runner OS protection.

## DEC-718 — Keep the persistent sibling witness valid only while creation remains unrevoked

The DEC-703 persistent sibling negative tracked `expected_sibling_created=True` once the correct regular-file `IN_CREATE` had appeared, but never cleared it. A subsequent `IN_DELETE`, `IN_MOVED_FROM` or `IN_MOVED_TO` involving **that same expected filename** can delete, relocate or substitute the created inode. Keeping the old create flag latched would allow `sibling_creation_control_detected=true` if the evaluator also received a purported correct final inventory and sibling snapshot, even though the event sequence contradicted the original creation's persistence.

The observer now clears the expected-sibling creation flag on a same-name delete, move, or directory-kind replacement; a genuinely new regular-file `IN_CREATE` can establish a new pending witness. Unrelated names do not clear that file-specific state, and the final inventory/inode checks and overall BLOCKED status remain mandatory.

Four new source-defined tests bring the suite to **195 methods**: same-name delete cancels the claim, move-out cancels, move-in cancels, and unrelated child activity preserves the event-specific claim (still overall BLOCKED). This is synthetic basename lifecycle consistency, not a kernel-authenticated inode lineage proof, OS enforcement, or authorization for the annual runner. Exact-head full regression and independent source/security review required.

## DEC-719 — Duplicate same-name create events invalidate event-stream completeness

The synthetic decoder previously held pending named `IN_CREATE` events in a set. Two consecutive `IN_CREATE` events for the **same regular child basename**, without an intervening deletion or move, collapsed into the same set entry. A later `IN_DELETE` could therefore satisfy a transient control, even though the same-name duplicate was inconsistent with a complete ordered observation of real directory-entry creation. A second create for the same existing entry needs an intervening removal/replacement to be a distinct valid event.

The decoder now marks the **entire stream malformed** when it encounters `IN_CREATE` for a still-pending regular-file basename. This does not authenticate Linux telemetry or prohibit legitimate unrelated names. A legitimate `CREATE → DELETE → CREATE → DELETE` sequence and a new create after same-name move remain supported. Four source-defined regression methods bring the suite to **199**. Two check that a duplicate target or unrelated basename cannot permit an affirmative transient negative claim, while two retain repeated properly separated controls. Deliberate mutation cases remain overall BLOCKED; Phase 3/full CI and independent security review are required.

This is an intentionally conservative consistency filter over fake bounded inotify records, NOT proof of real no-write OS isolation, loss-free kernels or annual runner permissions.

## DEC-720 — Require strictly boolean opt-in mode parameters before any setup

The executable CLI supplies boolean flags, but the directly callable `run_demo` helper previously evaluated `sum((negative, replace_watched_inode, create_sibling, transient_sibling))` without checking the argument types. Values such as `"true"`, `None`, lists, maps or `NaN` can raise unexpected `TypeError`, silently skip mode selection or cause unintended truthiness, instead of returning a deterministic **BLOCKED** receipt. This is an internal API robustness risk, not a confirmed annual runner defect.

The helper now requires exact `bool` for each of its four mode arguments before computing their sum, checking host readiness or creating a public disposable directory. Four new source-defined test methods raise the suite to **203**: malformed inputs in all mode positions, all mutually conflicting valid boolean combinations, invalid mode rejection before any directory setup, and valid boolean modes on an unsupported host. All malformed inputs fail closed. This does not change argparse, any installed workflow, file permission or trading system, and none of these new tests opt into a real Linux demonstration.

Review remains draft-only, with exact-head Phase 3/full regression and independent security source review needed.

## DEC-721 — Duplicate same-name deletes cannot be treated as a complete event stream

The same issue addressed for repeated `IN_CREATE` in DEC-719 affects `IN_DELETE`: two removals for the exact same directory-entry basename cannot both describe an unchanged complete timeline unless a new entry arrived between them. The prior decoder did not track pending deletes, so `DELETE(name) → DELETE(name)` remained syntactically well-formed, even though the stream could be missing a creation, rename, or other predecessor. If such a duplicate appeared alongside a valid-looking transient target pair, the evaluator could overstate `event_stream_complete` or negative-control detection.

The parser now tracks the most recent removal of each child name. A repeated `IN_DELETE` without intervening same-name `IN_CREATE` or `IN_MOVED_TO` marks the whole stream **not well formed**. A new child or move-in clears that deletion flag; a delete of an entry that already existed before the observer started remains acceptable. Four source-defined regressions bring the suite to **207 methods**: duplicate same-name deletes, duplicate unrelated delete poisoning otherwise expected evidence, a valid delete/create/delete timeline, and a valid delete/move-in/delete timeline. All negative controls still BLOCK and do not authorize dispatch.

The only independent spot-check was a separate public `/tmp` microprobe observing real `IN_CREATE, IN_DELETE, IN_CREATE, IN_DELETE` for one reused filename; it does not authenticate the observer or establish actual annual OS confinement. Full regression and qualified independent review remain necessary.

## DEC-722 — Require exact immutable bytes for decoded event buffers

The decoder previously used `isinstance(data, bytes)`. A Python `bytes` subclass can override methods such as `__len__` even though it inherits from `bytes`. A hostile synthetic caller could pass a subclass that raises when asked its length, triggering an uncontrolled exception, or spoofs a zero-length stream despite nonempty underlying bytes. That is not the shape returned by a genuine kernel `os.read`, and it does not establish a quiet observation.

The parser now requires **`type(data) is bytes`** before reading its length or unpacking any events. Three new source-defined methods increase the suite to **210**, covering a subclass with raising `__len__`, a subclass lying about its length, and a genuine plain-bytes file modification event that remains recognized. All malformed inputs return a fail-closed classification and overall BLOCKED when evaluated. The bounded collector already insists that `os.read` returns an exact `bytes` chunk.

This is synthetic Python input hardening only; no annual runner artifact, privilege, workflow, installed gate, broker or trading action is touched. Exact-head Phase 3/full regression and independent security review required.

## DEC-723 — Validate inotify collector FD and poll record types before equality

The DEC-690 collector checks that the only poll response compares equal to `(fd, select.POLLIN)`, but a patched or malformed element may implement `__eq__` that returns `True` while being neither a kernel `(int,int)` record nor normal `POLLIN` readiness. A `tuple` or `int` subclass can likewise spoof the equality comparison; without strict types, the collector could call `os.read` after fictitious readiness. Separately, the direct collector helper did not validate `fd` before registering, allowing non-integer or negative injected file descriptors to reach polling.

Now `_read_pending` requires a nonnegative exact Python integer FD before constructing a poll object and, for nonempty readiness, **one exact `tuple` containing exactly two exact integer values** before comparing against `(fd, select.POLLIN)`. Rejected shapes produce the existing handled fail-closed `OSError`, before any `os.read`. Four synthetic regressions raise the suite to **214 source-defined methods**: forged equality object, forged tuple subclass, bool/int subclasses or wrong tuple arity, and invalid FDs. Genuine `select.poll.poll()` emits a list of plain `(int,int)` pairs and retains prior behavior.

This tests untrusted Python collector input shape, **not** real OS write prevention, source provenance or dispatcher authorization. Phase 3/full exact-head CI and independent security review required.

## DEC-724 — Snapshot helper must reject impossible `os.read` return shapes

The disposable regular-inode snapshot already required a bounded file size and compared the returned byte count with stat metadata. But the result of `os.read(fd, st_size+1)` was not type-checked before `len(data)`; synthetic fault injection returning `None`, a string, list or hostile `bytes` subclass could raise an uncontrolled `TypeError` or a mocked length exception instead of the normal fail-closed `OSError` handled by the demo. In addition, an impossible mocked result longer than the requested count did not have a dedicated shape guard.

The helper now requires an **exact immutable `bytes` result no longer than the requested `st_size+1`** before consulting post-read metadata or accepting a snapshot. Invalid shapes raise a handled `OSError`. Four source-defined POSIX-gated methods bring the suite to **218 tests**, covering non-byte read results, hostile subclass, oversized mocked read, and actual generated regular-file bytes/inode identity. The generated /tmp demo and all annual runner hard stops remain unchanged; this does not authenticate read provenance or OS write prevention. Exact-head Phase 3/full regression and independent security review remain necessary.

## DEC-725 — Directory negative controls require the original source to stay unchanged

The persistent and transient sibling negative controls are intended to probe **directory-entry mutation while the generated `sample` source stays untouched**. Earlier checks validated the expected child event and final inventory but could mark `sibling_creation_control_detected` or `transient_directory_control_detected` true even when the original source's final bytes differed from baseline or its inode was replaced. Every such case already returned overall BLOCKED, but the specific claim of an *isolated directory-only negative* was overstated.

Both dedicated directory negative control predicates now also require strict equality of the original and final bounded public source bytes and `inode_stable is True` in addition to their existing named event, file-kind, intermediate-snapshot, final-inventory and event-stream completeness gates. Four new source-defined regression methods bring the suite to **222 tests**: changed source bytes and substituted source inode separately defeat persistent and transient sibling-control detection. Legitimate generated directory-only controls retain their existing BLOCKED outcomes.

These point-in-time assertions do not establish continuous OS source immutability, authenticated host observers or permission for annual runner dispatch. Exact-head CI and qualified independent review remain mandatory.

## DEC-726 — Enforce one strictly Boolean negative-control mode in direct evaluator

The public CLI and `run_demo` helper already ensure negative modes are mutually exclusive and strictly Boolean, but the standalone internal `_evaluate` helper accepts four flags representing the same incompatible deliberate controls without validating their types or exclusivity. A direct synthetic caller could request both a write/revert and sibling negative, or pass an injected truthy string/number, and receive potentially affirmative control fields for a scenario that the actual demo refuses to execute. The overall outcome was still BLOCKED, but the local evidence receipt could overstate what a single control observed.

The evaluator now rejects any non-`bool` of `negative`, `replacement_negative`, `sibling_negative` or `transient_sibling_negative`, and rejects more than one true flag **before parsing any event buffer**. Invalid combinations return ordinary deterministic BLOCKED results. Four additional source-defined unit methods bring the suite to **226 methods**, covering malformed values in all positions, all six two-mode conflicts, early gate before decoding, and a valid no-negative clean-but-unverified control. No real Linux demonstrations run in these tests.

This enforces consistency only between the toy evaluator API and its CLI, not authenticated Linux kernel evidence, real protected-runner isolation or run385 authorization. Exact-head Phase 3/full CI and independent security review remain required.

## DEC-727 — Disposable inotify watcher must not occupy standard descriptors

Linux allocates the lowest free file descriptor for `inotify_init1`. If a parent process previously closed stdin, stdout or stderr, the new inotify watcher may receive descriptor **0, 1 or 2**, crossing a standard-I/O trust and cleanup boundary for the toy observer. The prior code accepted these descriptors and later closed them as though they were ordinary isolated observer handles. This is not evidence of a real runner exploit, but it is a poor boundary for any experimental instrumentation.

The disposable `_start_watch` helper now closes and rejects any newly allocated FD in **0–2 before installing either watch**. The bounded `_read_pending` collector requires an exact Python integer FD greater than 2 before poll registration. Four new synthetic test methods bring the suite to **230**: reject STD FDs before poll, reject+close each mocked low inotify init FD without calling `inotify_add_watch`, allow a normal fake FD 17 with two distinct registered watches, and preserve the ordinary quiet poll control. All are fake/libc-mocked rather than real annual tasks.

This protects only the generated local experiment's standard-descriptor handling; DEC-650 still requires independently demonstrated actual stdio and OS confinement across all annual jobs, and DEC-651 remains a separate immutable one-shot admission blocker. Exact-head Phase 3/full regression and independent security review are required.

## DEC-728 — Track occupied names for both file and directory creates

DEC-719 rejected two unseparated regular-file `IN_CREATE` events for the same basename, but its pending set intentionally tracked only regular files used by the transient-file negative. A duplicate **directory** `IN_CREATE|IN_ISDIR`, or an impossible file-create followed immediately by a directory-create for the same still-present filename, could still be called a complete stream. Linux directory entries share a namespace regardless of whether they are files or directories; absent a removal or move-out, two independent same-name creations do not describe a coherent observed entry history.

The decoder now tracks **all observed newly occupied basenames**, including named directory creates and move-ins, while retaining the separate regular-file matching set. `IN_DELETE` or `IN_MOVED_FROM` clears occupancy; `IN_MOVED_TO` marks the arrival. A repeated `IN_CREATE` for an occupied name, regardless of `IN_ISDIR`, marks the entire buffered stream not well-formed. This is a bounded, conservative observation of events **since registration**, not a census of preexisting children.

Five new source-defined tests bring the suite to **235 methods**: duplicate directory-create, file→directory and directory→file creates without removal, legitimate directory delete followed by file creation, and illegal create after same-name move-in with no removal. Any malformed stream still BLOCKS and cannot credit a synthetic negative control. Exact-head Phase 3/full regression and independent source/security review required; this does not authenticate the kernel, prevent writes or resolve annual run385 admission.

## DEC-729 — Reject impossible observed file/directory kind transitions

DEC-728 records which child basenames were created or moved into a watched directory, but does not remember whether a newly observed entry was a **regular file or a directory**. A synthetic sequence `IN_CREATE(file-name) → IN_DELETE|IN_ISDIR(same-name)`, or a newly created directory followed by a same-name **file** `IN_MOVED_FROM`, was still reported as a well-formed complete observer stream, despite no intervening replacement to justify the changed entry kind. Such a sequence can misrepresent event completeness even though the overall result remains BLOCKED.

DEC-729 adds a separate per-name observed entry-kind dictionary. A child `IN_CREATE` stores `IN_ISDIR`; a matching `IN_DELETE` or `IN_MOVED_FROM` must have the same kind if that entry was previously observed. `IN_MOVED_TO` legitimately may replace an existing target and therefore replaces its kind record; a delete/move-out removes the record. A delete of a preexisting child whose kind has not been established is not rejected solely because its kind is unknown.

Six source-defined unit methods bring the suite to **241** tests, covering opposite-kind deletes, wrong-kind move-outs, valid paired file/directory lifecycles, a kind-changing move-in replacement, and preexisting deletion. These are bounded, local synthetic event-contract checks. They cannot verify inode identity or guarantee OS-enforced absence of writes, and do not authorize annual dispatch.

## DEC-730 — Move-out establishes known basename absence, just like delete

DEC-721 started tracking recent `IN_DELETE(name)` to reject a repeated delete without a new same-name entry. However, `IN_MOVED_FROM(name)` **also removes the entry from this directory** and previously did not update this absent-name state. Thus the observer could call `CREATE(name) → MOVED_FROM(name) → DELETE(name)`, `DELETE(name) → MOVED_FROM(name)`, or repeated move-outs a complete stream, despite no intervening `IN_CREATE` or `IN_MOVED_TO` to recreate the basename. DEC-715 had a synthetic test that even expected the first inconsistent sequence to be well formed, while correctly declining to credit its transient negative control.

The decoder now marks the basename as absent on every `IN_MOVED_FROM` and rejects either delete or move-out if it was already known absent. The existing `IN_CREATE` and `IN_MOVED_TO` clear the absent marker, allowing a new entry after move-out. The previous DEC-715 test is corrected to require malformed stream, not merely a declined witness. Five more source-defined tests bring the suite to **246 methods**, covering move-out→delete, delete→move-out, duplicate move-out, valid move-out/move-in/delete, and valid move-out/create/delete. All unsupported histories remain BLOCKED.

This extends only synthetic event-timeline consistency for disposable public fixtures. It cannot authenticate kernel provenance, prove observed watch continuity or establish annual OS isolation. Exact-head CI and independent source/security review remain required.

## DEC-731 — Reconcile pending observed child entries with final directory inventory

The disposable directory negative controls validate an exact final inventory of generated filenames, but their inotify event classifier did not expose names of **additional entries created or moved into the directory but never observed removed**. For example, a transient control could be marked detected after `CREATE(temporary-public-sibling) → CREATE(other) → DELETE(temporary-public-sibling)` even though the final inventory was supplied as `("sample",)`. An earlier synthetic positive fixture expected this contradiction to pass. Persistent-sibling evidence had the same issue if an additional child survived alongside `unexpected-public-sibling`.

The decoder now reports a sorted immutable tuple `pending_new_child_names` of child basenames known present from observed creates/move-ins since registration, updated by delete/move-out. The persistent directory control requires **exactly the named persistent child** pending; the transient control requires **no pending new child**, in addition to all existing exact event, source-inode, file snapshot, watcher and inventory checks. Early malformed-buffer returns supply an empty diagnostic tuple but still fail closed. This is deliberately limited to observed entries, not an independently trusted full filesystem census.

Five new source-defined tests bring the suite to **251 methods**: surviving unrelated child cannot be reconciled in transient or persistent controls, a fully removed unrelated child is allowed, the exact persistent child appears as the sole pending name, and malformed decoder returns carry no claimed pending names. The older positive synthetic fixture now includes deletion of its unrelated child so it matches its own stated final clean inventory.

This improves internal event-vs-inventory consistency only; it does not guarantee Linux provenance, trusted observation of missed events, or annual runner OS confinement. Exact-head Phase 3/full historical CI plus independent source/security review required.

## DEC-732 — Complete local observation requires two distinct installed watch IDs

The evaluator separately reported `both_watches_identified=false` when the directory watch was absent, malformed or aliased to the source-file watch, but its `event_stream_complete` property only examined parseability, overflow, invalidation and the local `watcher_alive` flag. Consequently the parser could call a **file-only quiet buffer a complete observation**, and a synthetic write/revert negative with two file-watch `IN_MODIFY` notifications plus intermediate snapshot could claim `negative_control_detected=true` despite never identifying the parent directory watch. Overall status remained BLOCKED due to a separate failed check, but those specific evidence labels were misleading.

DEC-732 computes a single strict `both_watches_identified` predicate and makes it a prerequisite for `event_stream_complete` and every specific negative-control detection claim. The parser's `well_formed` result continues to mean only valid *buffer syntax*, not continuous watch coverage. The earlier positive synthetic write/revert fixture is updated to explicitly provide the same second watch as the real disposable demo. Four new source-defined tests increase the suite to **255 methods**, checking absent directory watch, write/revert with a missing watch, aliased file/directory watch descriptors, and a valid dual-watch quiet local unverified observation.

These are two *local* inotify watch-descriptor values, not independently attested watcher registration or source isolation. A green unit test cannot authorize annual run385. Exact-head Phase 3/full regression and qualified security review remain required.

## DEC-733 — Source write/revert negative requires no directory-entry changes

The write/revert control is meant to exercise deliberate edits of the existing public `sample` inode and restore its exact original bytes, *without* changing the generated parent directory's entry structure. DEC-732 required both source and directory watches, yet `negative_control_detected` could remain true if the same synthetic event stream contained another child's create/delete, or the final directory inventory had extra files, provided two source `IN_MODIFY` records and a midpoint flag were supplied. The overall result was already BLOCKED, but the specific claim that the write/revert control ran in isolation was overstated.

The evaluator now shares a single `directory_intact` property with its existing `no_directory_entry_mutations` check and requires it for the dedicated write/revert negative detection: zero observed directory mutation events, exact Boolean `directory_inventory_ok=True` and exact tuple `("sample",)` as the sampled final directory names. Five earlier positive synthetic write/revert fixtures are updated to supply the explicit final sample-only inventory already generated by the real demo. Four new source-defined methods bring the suite to **259 tests**, covering persistent unrelated create, transient unrelated create/delete, missing/wrong-typed final inventory, and unchanged parent with the expected local source write/revert observation.

This is **not** continuous kernel audit or trusted OS-enforced source immutability, merely internally consistent disposable evidence accounting. Real annual run385 remains blocked pending independent OS and exclusive server-side admission proof. Exact-head Phase 3 and full historical regression plus qualified review required.

## DEC-734 — Directory-only negatives cannot include watched source-write events

DEC-725 required matching original/final public source bytes and inode for sibling-directory negative controls. But a **write and restoration of the watched source inode** can leave its bytes and identity unchanged while generating `IN_MODIFY` or `IN_CLOSE_WRITE`. The evaluator could still claim a successful *directory-only* persistent or transient sibling control even though the same event stream recorded source-file write activity. Every such run already BLOCKED overall, but its specific evidence attribution was too permissive.

DEC-734 requires **zero `source_content_write_events` on the source-file watch descriptor** for both sibling-directory control predicates. It does **not** reject a directory-watch `IN_CLOSE_WRITE` record for the generated sibling, which is expected when writing the public child file and was never a write to the source inode. Four new source-defined methods bring the suite to **263 tests**: persistent sibling with watched source `IN_MODIFY` or `IN_CLOSE_WRITE` cannot claim directory-only control, transient sibling with source modification cannot claim it, and a transient sibling's own directory-watch close-write remains a valid (still BLOCKED) control observation.

This prevents internally contradictory synthetic evidence labels, not real write/restore races, untrusted host logging, or any annual-runner permission risk. Exact-head Phase 3/full historical CI and qualified security review still required.

## DEC-735 — Kind-changing rename target requires observed prior departure

DEC-729 began tracking whether newly observed directory entries were files or directories but allowed an `IN_MOVED_TO` record of the opposite kind to unconditionally overwrite the tracked entry kind **without any preceding deletion or move-out**. That accepted a synthetic file→directory rename replacement which ordinary Linux `rename(2)` rejects with `ENOTDIR` (and the reverse with `EISDIR`). A DEC-729 synthetic test incorrectly treated the kind change as automatically legitimate. The more advanced `renameat2(RENAME_EXCHANGE)` operation can swap different kinds, but in a separately generated Linux `/tmp` microprobe exchanging a file and directory it emitted **matching move-out then move-in** records for each watched name.

DEC-735 treats `IN_MOVED_TO` of an opposite kind to a still-tracked occupied name as a malformed/incomplete stream unless a prior `IN_DELETE` or `IN_MOVED_FROM` removed the old kind. Moving in over an already occupied **same-kind** target remains supported for normal rename replacement. The old positive synthetic fixture is corrected to include the observed move-out. Four new source-defined methods increase the suite to **267 tests**, covering both opposite-kind mismatches, ordinary same-kind rename replacement, and a legitimate move-out then opposite-kind move-in. This conservative toy event contract does not prove independent host event provenance or OS confinement.

The isolated microprobe is not execution of annual protected jobs or of the five manually opted-in repository demos. Exact-head Phase 3/full historical CI and qualified independent review remain required.

## DEC-736 — Exact plain strings required in final inventory tuple

The evaluator already required `type(directory_inventory_names) is tuple` but never validated element types. Python tuple equality invokes the elements' `__eq__` methods, allowing a synthetic caller to pass `(AlwaysEqual(),)` or `(ForgedStrSubclass(),)` which compares equal to the expected `("sample",)`. The quiet original-directory predicate could therefore be spoofed while the overall verdict appeared locally unverified; persistent sibling evidence likewise used tuple equality against two expected names. The actual disposable directory's `Path.name` values are plain built-in strings, so such injected elements are not plausible kernel/file enumeration output.

DEC-736 computes one `inventory_names_are_plain` prerequisite: an exact tuple with **every element of exact type `str`** before trusting any final inventory equality. The quiet-directory, persistent sibling and transient directory checks use this same prerequisite. Four new source-defined tests bring the suite to **271 methods**: hostile always-equal element, forged str subclass, expected sibling impersonator, and preserved plain-string local unverified control. All malformed inputs remain BLOCKED and cannot authorize dispatch.

This repairs only a local untrusted Python input contract, not host audit authenticity, OS-enforced write prevention or annual run385 eligibility. Independent qualified review plus exact-head Phase 3/full CI remain mandatory.

## DEC-737 — Repair inherited full-CI test-contract mismatches without rewriting failed PRs

Exact-head full historical regressions **#898–902, #904 and #906 completed FAILURE** despite Phase 3 success. Source-defined CI log review found two inherited test-contract errors, neither a demonstrated bypass of the observer: DEC-727 changed a correct fail-closed `_read_pending` error message to `"requires a nonstdio integer fd"` while the older invalid-FD regression still expected the outdated `"requires an integer fd"`; DEC-731 made an unrelated child genuinely disappear before final inventory, so its synthetic stream now contains **two** file `CREATE→DELETE` pairs, while the old test still expected the generic pair counter to be **one**. The exact targeted negative-control pair count is nevertheless **one**, as intended.

DEC-737 corrects the two stale assertions in the disposable unit tests without changing observer implementation. Two explicit regressions verify all generic paired names vs one exact target and that invalid FD 0–2/noninteger values retain the expected blocked/no-poll contract. This brings the suite to **273 source-defined tests**. Prior failing CI runs remain permanently RED at their old heads; this strictly stacked new child requires its own fresh successful exact-head Phase 3 and full historical regression before acceptance. More failures on older heads may still need separate review.

No FMP annual job, protected source, installed workflow/ruleset, broker or runner is accessed. This is internal synthetic test maintenance, not independent source immutability proof; DEC-650/651 remain BLOCKED.

## DEC-738 — Do not call missing or malformed coverage "no observed writes"

The evaluator's `no_observed_writes` property previously compared the decoder's `write_events == 0` counter **without establishing that the local kernel event stream was complete**. The malformed-buffer early exit intentionally returned zero event counters; consequently an incomplete, overflowed, invalidated, dead-watcher or missing directory-watch observation could claim `no_observed_writes=true`. Although a separate required check kept overall status BLOCKED, that affirmative observation was misleading.

The property now requires **two distinct valid watch IDs, complete parse, no overflow/invalidation, living local watcher and zero write notifications**. It uses exactly the safety boundaries already established for `event_stream_complete` and does not change the criterion for a genuine locally quiet case. Four source-defined regression methods bring the suite to **277 methods**: truncated buffer, missing directory watch, dead watcher and complete dual-watch quiet observation. The last case remains `LOCAL_DISPOSABLE_WITNESS_UNVERIFIED`, never authorization. This is synthetic metadata accounting, NOT proof that a kernel has independently prevented writes or issued authenticated host telemetry.

DEC-737's two inherited stale test fixtures were corrected in the immediate parent draft #908; those historical red ancestors remain red. Exact-head Phase 3, full historical regression and qualified independent security review remain required.

## DEC-739 — Reject standard descriptor reuse in generated regular-file snapshots

DEC-727 rejected `inotify_init1` watcher FDs 0–2 to avoid occupying or subsequently closing a closed standard descriptor. But the same risk existed in the separate `_snapshot_regular` helper: it directly used `fd=os.open(path,...)` then `os.close(fd)` in its finally block. If a parent process closed stdin/stdout/stderr, Linux could allocate the snapshot file on 0–2. The toy helper would later close or repurpose what would normally be process standard I/O. This did **not** authorize dispatch or prove any actual annual runner exploit, but it was inconsistent with the established disposable FD boundary.

DEC-739 requires a valid exact integer nonnegative snapshot FD and refuses descriptor 0, 1 or 2 **before any fstat, read or other inode handling**, closing a newly allocated low FD exactly once. Malformed synthetic return types fail closed without attempting to close a non-FD object. Three source-defined regression methods increase the suite to **280 methods**: mocked allocated low FDs, malformed mock FD returns, and a normal no-follow snapshot of generated public content. This does not introduce any protected OS paths or installed workflows. Independent exact-head Phase 3/full CI, real host-level OS isolation and security review remain necessary.

## DEC-740 — Validate libc inotify registration return shapes at the API boundary

The local Linux observer sets `ctypes` `restype=c_int` for `inotify_init1` and `inotify_add_watch`, so a real libc call returns integer FDs/WDs. Synthetic test/fault injection of those functions, however, can return `None`, booleans, strings, floats, or values outside signed-32-bit watch descriptor range. The previous observer compared those values with `< 0` without type validation, potentially throwing a non-fail-closed `TypeError` outside the demo's handled `OSError` family or propagating false watch identity. This does not imply an actual libc type failure; it is a direct helper robustness gap.

DEC-740 validates exact integer descriptor identity immediately after `inotify_init1`, and exact signed nonnegative integer watch IDs for each `inotify_add_watch`, closing the already allocated observer FD once on any invalid file/directory watch identity. Four source-defined methods bring the suite to **284**: injected invalid inotify-init FD types, invalid first watch types/out-of-range, invalid directory watch including alias, and a normal two-watch integer result. Only the synthetic /tmp observer changes, never the protected annual jobs or installed workflows. Exact-head Phase 3/full historical CI and independent security review remain necessary.

## DEC-741 — An unexecuted negative-control mode is not a detected control

The local evaluator historically set the mode-specific `negative_control_detected`, `sibling_creation_control_detected`, `transient_directory_control_detected`, `midpoint_source_snapshot_matches_expected` and `transient_midpoint_regular_file_verified` flags to **True when that negative-control mode was disabled**. This was convenient for a single `all(checks)`-style requirement list, but it was a substantive semantics error: a clean toy observation with **no negative control run** reported detection of all negative modes. It also overstated unrelated negative detection when the caller exercised only one control.

DEC-741 separates evidence from requirement applicability. Each mode-specific Boolean is **False when its mode is not selected**, meaning `not observed/not executed`, and the findings generator ignores those inactive checks instead of treating them as missing requirements. Selected modes still require exact proof conditions and still append deliberate BLOCKED findings. General source identity, directory inventory, watcher completeness, and quiet-event checks are unchanged. Five source-defined test methods raise the suite to **289**: mode-free quiet observation makes no spurious claims and remains local-unverified; source rewrite, persistent sibling, transient sibling and inode-replacement modes each report only their own appropriate evidence. No control authorizes dispatch.

This only improves transparency of self-generated public event receipts, not independent kernel attestation or annual OS confinement. Exact-head Phase 3/full historical CI, qualified independent review, and separately controlled real OS isolation/admission gates remain necessary. The failed CI ancestors #898–902, #904 and #906 remain red; a strict descendant #908 fixes two inherited stale test assertions but cannot alter historical runs.

## DEC-742 — A directory-only negative requires no source inode metadata mutation

DEC-734 required zero original-source content-write events for persistent/transient sibling negatives, but the Linux source-file watch can also report `IN_ATTRIB` on source inode chmod/ownership/time/metadata changes. Such metadata activity can occur without changing baseline/final sampled bytes or replacing the inode. The prior evaluator could still credit an isolated *directory-only* negative despite its own source watch recording metadata mutation. Every result remained BLOCKED, but the mode-specific evidence label overstated the isolation of the deliberate control.

DEC-742 tracks `source_attribute_events` from `IN_ATTRIB` on the **original source file watch ID only**, and requires its counter be zero alongside `source_content_write_events` in both sibling-negative detection predicates. An attribute event observed on the *directory watch* for a generated child remains distinct; it must not impersonate a source-inode metadata change. Four new source-defined tests bring the suite to **293 methods**: persistent source metadata activity invalidates isolated control detection, transient source metadata activity invalidates, generated-child directory-watch attribute notification does not count as source mutation, and invalid decoder return remains fail closed with zero diagnostic count.

This is toy /tmp event attribution, not independent host kernel telemetry or protection against unobserved write races. DEC-650/651 annual isolation and immutable admission remain BLOCKED. Exact-head Phase 3/full regression and independent source/security review required.

## DEC-743 — Do not assert quiet directory inventory without a complete local event stream

An exact final generated inventory `("sample",)` and zero `directory_changes` in a truncated/incomplete event buffer did not prove no intervening directory mutation. Yet the evaluator's `no_directory_entry_mutations` property was True whenever the parsed counter was zero and the final sampled name tuple matched, even if the event decoder reported overflow/malformed watch input or the collector was dead. The overall verdict remained BLOCKED due to other checks, but the standalone "no directory entry mutations" evidence claim was overstated.

DEC-743 adds the same prerequisites as `event_stream_complete` to the shared `directory_intact` predicate: two distinct source/directory watches, well-formed complete buffer, no overflow or invalidated watch, living collector, zero observed directory entry changes, and an exact plain-string final inventory of just the original public sample. This also ensures the source-write/revert negative, which requires `directory_intact`, cannot claim isolated operation when directory observation is incomplete. Four new source-defined tests bring the suite to **297 methods**: truncated record, dead watcher, missing parent watcher, and valid complete local quiet inventory (still local-unverified and nonauthorizing).

This does not constitute independently verified OS no-write confinement or unforgeable kernel provenance. The real DEC-650/651 annual runner gates remain BLOCKED, with exact-head full regression and qualified independent security review required.

## DEC-744 — Bound synthetic final inventory size before inspecting member types

DEC-736 made sampled final inventory members strictly plain strings before tuple equality, preventing equality spoofing. The direct evaluator nevertheless accepted an **unbounded tuple** from a synthetic caller and visited every element with `all(type(name) is str for name in ...)`, even when there were thousands of names and the final exact expected tuple could never match. The actual generated disposable-demo accepted success shapes are only `("sample",)` or `("sample","unexpected-public-sibling")`; extra entries always BLOCK. Requiring a bounded shape before traversing candidate values is consistent with the model's bounded evidence and diagnostic limitations.

The evaluator now requires an exact tuple of **one or two** elements *before* checking each member is an exact `str`. Larger inventories fail the quiet/negative evidence predicates immediately rather than scanning their contents. Two new source-defined methods bring the suite to **299 tests**: a large 2,001-name injected inventory cannot claim quietness, while the exact two-name persistent sibling control remains recognizable yet overall BLOCKED. No protected data is involved and this does not guarantee authenticated kernel provenance or annual OS confinement. Full exact-head CI and independent security review remain required.

## DEC-745 — Bound Linux observer FD integers to signed 32-bit range

DEC-727/739/740 required exact integer nonstdio file descriptors from libc and `os.open`, but allowed an arbitrarily large **exact** Python integer from an injected helper or `os.open` mock. Real Linux file descriptors are represented by signed C `int` and therefore do not exceed `INT_MAX=(1<<31)-1`; an injected `1<<64`-style value cannot be a valid open Linux handle and can cause `OverflowError` when passed to `select.poll.register`, `os.fstat`, or a ctypes function instead of a deterministic fail-closed receipt.

DEC-745 defines `MAX_FILE_DESCRIPTOR`, validates the typed return of `inotify_init1` before installing watches, rejects oversized IDs from `_read_pending` before polling, and rejects oversized mock snapshot FDs before `os.fstat`. Three source-defined tests bring the suite to **302 methods**: impossible FD in event collector, impossible snapshot FD, and impossible fake libc FD without watch registration. Invalid synthetic FDs never authorize; genuine POSIX FDs retain prior functionality. This is local API-boundary robustness, not real host OS confinement or annual dispatch authorization.

## DEC-746 — Bound actual generated-directory inventory enumeration

DEC-744 capped the **evaluator's** supplied inventory at two exact names, but the real disposable runner still built an unrestricted tuple using `Path.iterdir()` before calling the evaluator. This needlessly scanned and allocated a potentially large directory even though a third observed entry already disqualifies both the clean one-name result and the expected two-name persistent-sibling result.

The collector now uses context-managed, lazily consumed `os.scandir` and reads **at most three names**, checks each is a plain string before sorting, then passes that bounded tuple to the unchanged fail-closed evaluator. One or two actual names preserve the previous controls; three names always BLOCK rather than claiming an intact directory. Three new source-defined tests raise the suite to **305 uniquely named methods**: generated one/two-name inventories, an injected iterator that would fail if a fourth child were read, and a hostile entry name rejected before sorting. This is bounded local enumeration, not authenticated kernel proof, annual runner OS isolation or dispatch admission. Exact-head Phase 3, full historical CI, and independent security review remain required.

## DEC-747 — Reject malformed snapshot fstat metadata before using it

The local snapshot helper previously checked that an opened handle was an exact integer FD, but could still trust synthetic `os.fstat` return fields of arbitrary types. A forged `st_size` could reach comparisons or `os.read` arithmetic, while a custom `st_ino` equality operator could falsify a before/after inode comparison. These objects are not produced by the ordinary kernel API, yet the defensive direct helper must fail closed when patched.

DEC-747 validates that **both** first and second fstat reads expose exact integer mode/device/inode/size/mtime_ns/ctime_ns fields and that the inode is a bounded regular file. It checks field shapes before size arithmetic or metadata equality. An invalid initial result is rejected before `os.read`; an invalid final result is rejected before returning data, with the already-open valid FD closed through `finally`. Three regression methods bring the suite to **308 unique tests**: noninteger first-stat fields, a hostile inode equality operator, and malformed second-stat metadata after a bounded read. Existing real public regular-file snapshots remain supported. This is local test-boundary integrity, not host OS isolation or authenticated annual evidence.

## DEC-748 — Revalidate watch registration at runner boundary

Although `_start_watch` itself rejects malformed libc watch IDs and stdio file descriptors, the executable `run_demo` previously unpacked and trusted its Python helper return. In a synthetic patched case, a helper yielding FD 0–2 could still cause `run_demo` to close a standard I/O descriptor in `finally`. Similarly, an aliased or malformed pair of watch IDs could reach the baseline snapshot before the evaluator later refused its quietness claim.

The runner now requires an exact three-member tuple of a plain nonstdio bounded integer FD and two distinct nonnegative bounded plain integer watch IDs **before** snapshotting. A malformed FD/tuple is rejected without closing unknown/stdio values. When the FD is valid but the watch identities are not, it is closed through the existing `finally` path. Three new source-defined regression methods increase the suite to **311 unique methods**: patched stdio FD does not close stdio or read samples, aliased WDs close an actual valid pipe FD without snapshotting, and a list-shaped registration cannot reach the snapshot. This is defensive handling for injected helpers and makes no annual-runner authorization claim.

## DEC-749 — Validate helper-produced snapshot tuples at every consumer

DEC-747 validates actual `os.fstat` values inside `_snapshot_regular`, but `run_demo` formerly trusted the return value of the *Python snapshot helper*. When the helper is patched for regression testing, a custom device/inode equality object, `bool` inode value, oversized bytes, or malformed identity tuple could reach the runner's before/after equality and negative-control logic. In particular an identity object with `__eq__` could forge `inode_stable=True` without any kernel observation.

DEC-749 adds one strict `_checked_snapshot_result` boundary on **all** generated source, midpoint, sibling and transient snapshot consumers. The helper requires an exact two-member tuple holding an exact pair of nonnegative integer device/inode IDs plus exact bounded bytes (at most 4,096). Invalid synthetic returns produce `OSError` and a blocked receipt, with valid installed watch descriptors still closed in `finally`, before stream drainage or fabricated identity claims. Three new source-defined regression methods bring the suite to **314 uniquely named tests**, including direct malformed shapes and forged equality plus injected first/final snapshot failures. This is robustness against synthetic helper substitution, not independent Linux observer authentication or annual isolation.

## DEC-750 — Distinguish standard-FD safety from temporary cleanup in synthetic tests

The DEC-748 patched-stdio regression initially mocked all `os.close` calls and asserted there were none. That accidentally conflates the inotify watch descriptor with unrelated, legitimate `TemporaryDirectory`/filesystem cleanup descriptors. The child test now wraps the real close operation to preserve cleanup and asserts the *specific injected fd 0–2* is never closed by the disposable runner. The production source is unchanged. One additional source-defined regression method injects a watch identity whose `__eq__` raises if called, verifies the invalid type is rejected before snapshot or comparison, and checks that a valid observer pipe FD is still closed. The suite now has **315 uniquely named test methods**. This is a proactive test-contract correction; it neither changes any completed historical CI nor claims annual authorization.

## DEC-751 — Validate void result of inotify poll registration

The disposable collector already verifies that poll readiness records are exact tuples matching the single monitored FD. Its `poller.register` return was previously ignored, so a patched poll object could claim a quiet result even after returning a malformed success status. The genuine Python `select.poll().register` API mutates the registration set and returns **None**; unexpected values cannot establish the required single-watch collection setup.

DEC-751 now requires `poller.register(...)` to return exactly `None` before polling, rejecting boolean/integer/string/custom-comparison results with a controlled `OSError`. Two new source-defined methods bring the disposable suite to **317 uniquely named tests**: malformed nonvoid registration values never reach polling or reads, and a custom object whose equality pretends to match `None` is also rejected. Existing real poll registrations and clean synthetic `register(...): pass` mocks remain valid. This is local collector API-shape defense, not authenticated OS write denial, independent host protection or annual admission.

## DEC-752 — Assert the generated public source fixture matches both snapshots

The disposable runner creates its own public `sample` file using the fixed `BEFORE` bytes. Although it already enforced bounded regular-file snapshots and equality of before/after data, it had not required the observed baseline to equal the **known generated fixture**. When a synthetic replacement of the snapshot helper returned different yet identical initial/final bytes, the runner could report local quietness despite never inspecting the expected generated sample.

DEC-752 now requires the baseline snapshot bytes and final snapshot bytes to equal the exact generated `BEFORE` fixture. Any mismatch raises handled `OSError` before starting deliberate negative controls or performing the final inventory/queue claims, and the installed watch FD closes. Two new source-defined regression methods bring the suite to **319 uniquely named methods**, covering unexpected baseline and final synthetic snapshot bytes. Legitimate generated control, write-and-revert, inode substitution, and sibling tests preserve their expected `BEFORE` payload. These are local fixture-consistency checks and cannot authenticate the watcher or authorize annual run385.

## DEC-753 — Close allocated inotify FDs if a watch registration raises

`_start_watch` already closed its nonstdio FD on negative or malformed watch-ID returns. However, a ctypes wrapper or injected `inotify_add_watch` call could also **raise** before either registration finished. Because `run_demo` receives the FD only after both watch registrations succeed, its outer cleanup cannot release that partially initialized FD. DEC-753 centralizes ownership of the allocated FD through the two registration calls. Both invalid return codes and raised exceptions close the FD exactly once; unexpected Python exceptions become handled `OSError` after cleanup. Normal complete dual-watch registrations still transfer ownership to `run_demo`.

Three source-defined tests increase the suite to **322 uniquely named methods**: first registration raises, directory registration raises, and an unexpected wrapper exception converts to a controlled error after closing the allocated FD. This reduces synthetic observer resource leaks, not evidence gaps in independent OS-enforced annual isolation or immutable dispatch admission.

## DEC-754 — Normalize unexpected snapshot API exceptions into handled local failures

DEC-753 covers raised watch-registration exceptions after allocating the observer FD. Its counterpart at the snapshot boundary still exposed injected Python exceptions from `os.open`, `os.fstat`, or `os.read` as unhandled `RuntimeError` rather than the disposable runner's handled `OSError` path. Real POSIX failures are already OSError, but fault-injected wrappers must not bypass fail-closed JSON results.

DEC-754 catches unexpected ordinary exceptions around opening and around the bounded read/stat block, preserves existing OSError behavior, converts other exceptions to controlled OSError, and closes an already valid opened descriptor exactly once in `finally`. If open failed, it never closes an unallocated handle. Three new source-defined regression methods bring the suite to **325 distinct test methods**, verifying unexpected errors from `os.open`, `os.fstat`, and `os.read` with the correct cleanup. The annual-runner authorization fields remain unchanged and no protected file is accessed.

## DEC-755 — Normalize unexpected bounded directory scan wrapper failures

The disposable runner now reads at most three entries through `os.scandir`, but injected scanner constructors, entry objects or iterators could raise ordinary Python exceptions that bypass `run_demo`'s handled `OSError` failure path. The scan helper now keeps the bounded three-entry limit and existing exact-name checks, while converting unexpected scanner-construction or enumeration exceptions into handled `OSError`. Genuine `OSError` exceptions retain their original shape.

Two new source-defined tests bring the suite to **327 unique test methods**: one patched scanner constructor raises; another iterator yields a valid first name and then raises. Both refuse inventory evidence without visiting more children or reporting a quiet observation. Real generated one/two-name directories are unchanged. This is synthetic API-boundary robustness, not authenticated kernel observation or annual OS write-prevention.

## DEC-756 — Normalize unexpected disposable event collector wrapper exceptions

A previous guard validates that `poller.register` returns None and that poll-readiness records have exact kernel-ready shapes. Yet patched `select.poll` factories, `poll` methods, or `os.read` wrappers can throw unexpected ordinary Python exceptions instead of legitimate `OSError`, bypassing `run_demo`'s fail-closed receipt handler. DEC-756 keeps the existing `_read_pending` API and byte/drain bounds, moving its implementation into `_read_pending_checked` with a narrow adapter around it. The adapter preserves original `OSError` behavior and converts other ordinary exceptions into handled `OSError`.

Three new source-defined tests bring the suite to **330 distinct test methods**: injected poll factory failure, readiness failure, and read failure. Each refuses an event stream with the expected call count rather than claiming a quiet observation. This only hardens generated local instrumentation against mocked wrappers and does not prove OS-enforced write denial, independent kernel event provenance, or immutable annual run385 dispatch.

## DEC-757 — Bound synthetic Linux stat device and inode identifiers

The DEC-747 first/final fstat validation and DEC-749 snapshot helper result guard require plain nonnegative integer device/inode IDs, but still accepted arbitrarily large exact Python integers (for example `1 << 64`) that cannot fit in Linux's unsigned 64-bit `st_dev` or `st_ino` fields. Such impossible injected IDs cannot establish believable local inode provenance, even when a patched helper returns the same large number twice.

DEC-757 defines `MAX_KERNEL_STAT_ID=(1<<64)-1` and applies the same 0..UINT64_MAX bound both to direct `os.fstat` metadata and to every higher-level injected snapshot helper result. Three source-defined methods bring the suite to **333 uniquely named tests**: oversized device/inode fstat values fail before read and close the valid FD, oversized helper IDs fail closed, and valid synthetic UINT64_MAX boundary values remain supported. Normal generated kernel IDs are unchanged. The bounds are not proof of independent OS protection or immutable run admission.

## DEC-758 — Normalize unexpected inotify library and initialization wrapper failures

The registration path now closes its allocated FD when either watch-registration operation raises, but a patched `ctypes.CDLL` constructor, callable signature setup, or `inotify_init1` invocation could still raise an unexpected ordinary Python exception **before the initializer returned any descriptor**. That would escape the runner's handled error path. DEC-758 wraps only the no-FD-owned setup and initialization stage, preserving genuine `OSError` and converting non-OSError failures into handled `OSError`. There is deliberately no close attempt before a valid FD is returned.

Three source-defined methods increase the suite to **336 unique tests**: unexpected library-loader failure, unexpected init-wrapper failure, and preservation of the original native `OSError.errno`. Existing stdio refusal, normal dual watch registration and resource ownership semantics are unchanged. This improves local fault-injection correctness only; it does not establish independent annual runner OS enforcement or immutable admission.

## DEC-759 — Require a nonzero rename cookie on synthetic directory moves

The parser already rejects a nonzero rename cookie on write/create/delete actions, but accepted a `IN_MOVED_FROM` or `IN_MOVED_TO` child event with cookie zero. Linux uses a nonzero rename cookie to correlate these move actions. An injected zero-cookie move cannot be considered a faithful complete kernel event sequence even when the name, watch descriptor and final inventory otherwise look plausible.

DEC-759 requires a nonzero cookie for both directory move directions. Three source-defined regression methods bring the suite to **339 uniquely named tests**: either standalone zero-cookie move is an incomplete stream, a two-record zero-cookie move sequence cannot be accepted as complete, and nonzero-cookie move records preserve existing accounting. The change does not attempt to equate a matching or mismatched cookie pair with independent kernel provenance. Real generated sibling and temporary controls remain unchanged. This is a narrow fail-closed record-layout check, not actual OS confinement or annual authorization.

## DEC-760 — Refuse impossible synthetic file-mode widths before treating an inode as regular

A forged fstat result could supply an arbitrary-width integer `st_mode` with regular-file type bits in its low half. `stat.S_ISREG` masks those low type bits, meaning the earlier plain-integer and regular-file checks could accept a value wider than the Linux 32-bit `mode_t` ABI. DEC-760 requires the initial and final fstat mode field to be in `0..UINT32_MAX` before evaluating its regular-file type. Other metadata and FD checks remain intact.

Two new source-defined tests bring the suite to **341 unique test methods**: negative or oversized synthetic mode fields fail before `os.read` and close the allocated FD, and a legitimate generated regular-file mode remains acceptable. This is a synthetic fstat boundary check and does not authenticate a kernel observation or establish annual OS isolation.

The previous DEC-759 rename-cookie check is a deliberately fail-closed record-shape rule: zero-cookie move records are treated as uncertain even if some unusual kernel corner case might produce them. The inotify manual associates cookies with rename events but this local decoder is not independent kernel proof.

## DEC-761 — Reject duplicate rename directions for one inotify cookie

The disposable parser now treats zero-cookie move records as uncertain, but did not validate *repeated uses* of a nonzero rename cookie. The kernel uses a cookie to associate the one `IN_MOVED_FROM` and one `IN_MOVED_TO` event from a rename. A bounded injected stream containing two `IN_MOVED_FROM` or two `IN_MOVED_TO` records under the same cookie should not claim a coherent rename timeline, even if the two filenames differ.

DEC-761 remembers, within the already bounded event byte buffer, which direction was observed for each nonzero cookie. A duplicate direction makes the overall stream malformed. A normal matching move-from/move-to pair remains accepted, as do unpaired directions because the other rename event may lie outside this watch. The check does not demand adjacent records or claim authentication of cookie values. Three new source-defined methods raise the suite to **344 distinct test methods**: duplicate move-from rejection, duplicate move-to rejection, and preservation of ordinary paired-cookie parsing. This does not establish a trusted independent event source or OS-level annual write prevention.

## DEC-762 — Refuse zero as a Linux inotify watch identity

The inotify add-watch API specifies nonnegative return values, while the Linux inotify manual's watch-ID allocation notes describe normal watch IDs being allocated in the range **1 to INT_MAX**. The disposable source previously accepted exactly zero as a synthetic file or directory watch ID. A patched helper returning zero could therefore claim a complete dual-watch registration even though a real current Linux watch allocation does not yield that identity.

DEC-762 requires IDs in `1..INT_MAX` at all eight local validation occurrences: initial event decoder, supplied directory watch, evaluator's two-watch completeness predicate, both C return values, and runner-boundary assertions. An injected zero result fails before snapshot, and a valid already-allocated inotify FD is closed on rejected registration. Four new source-defined methods increase the suite to **348 distinct test methods**, covering both direct zero-watch shapes, C registration cleanup and runner pre-snapshot refusal. This is deliberately conservative synthetic identity validation, not independent OS attestation.

## DEC-763 — Preserve validated regular-file mode in before/after fstat comparison

The snapshot helper validates that each fstat result is a bounded regular-file mode, but its canonical comparison tuple previously discarded `st_mode` and compared only device, inode, size, mtime_ns and ctime_ns. A synthetic before/after pair with changed permission bits and forged unchanged timestamps could therefore pass the consistency test despite a real metadata difference.

DEC-763 includes the validated mode in the canonical six-part stat tuple and compares it across both observations. It updates the bounded read-size index while keeping the externally returned snapshot identity as `(device, inode)`. Two new regression methods raise the suite to **350 uniquely named tests**: an otherwise identical mode change is rejected with FD cleanup, and unchanged mode still returns the original device/inode and payload. The direct metadata-contract assertion is adjusted to match the new six-part tuple without relaxing any check. This catches injected mode drift but does not prove the absence of races or independently authenticate host write denial.

## DEC-764 — Validate the encoded byte shape of inventory basenames

DEC-746 bounds live `os.scandir` enumeration to three entries. The previous scanner and direct evaluator then checked exact Python `str` types, but permitted synthetic names that no Linux `DirEntry.name` from a single directory component could represent, such as a 256-byte UTF-8 filename, embedded slash or NUL, `.`/`..`, or an unencodable surrogate.

DEC-764 adds `_plausible_inventory_basename` to check exact Python `str` and native `os.fsencode` roundtrip into a nonempty Linux basename of at most 255 **encoded bytes**, excluding slash, NUL and dot/dotdot names. Both bounded scanner and direct evaluator use the same predicate, with unexpected injected encoding failures treated as negative evidence rather than allowing exceptions to authorize. The scanner validates before sorting and still enumerates no more than three entries. The direct evaluator refuses impossible names before deriving quiet-directory claims. Valid surrogate-escaped names derived from real arbitrary-byte Linux filenames are still allowed. Three new source-defined regressions bring the suite to **353 uniquely named test methods**.

This is local synthetic inventory coherence, not kernel-origin authentication, independent OS write prevention, or annual-runner authorization.

## DEC-765 — Fail closed on unexpected generated runner mutation-wrapper exceptions

The disposable observer's individual inotify-registration, snapshot, event drain and bounded scan helpers already normalize unexpected ordinary Python wrapper errors into handled `OSError`. However, `run_demo` itself makes several public `/tmp` fixture mutation calls: `Path.write_bytes`, `os.replace`, write/revert file operations and `os.fsync`. With a patched Python wrapper, an ordinary `RuntimeError` could bypass the runner's final `except (OSError, AttributeError, ValueError)` and emit no fail-closed JSON receipt.

DEC-765 broadens only the **disposable runner's final error boundary** to ordinary `Exception`, keeping the same `BLOCKED` receipt and existing nonstdio FD `finally` cleanup while not suppressing `KeyboardInterrupt` or `SystemExit`. Three new source-defined regression tests increase the suite to **356 uniquely named methods**: a generated-source creation wrapper failure happens before any watch; a replacement wrapper failure blocks with the valid pipe observer FD closed; and a reverted-write `fsync` wrapper failure also blocks and closes the observer FD. This is local defensive fault-injection handling, not production permission or OS confinement.

## DEC-766 — Refuse impossible Linux snapshot nanosecond time fields

DEC-747 enforces exact `int` types on `st_mtime_ns` and `st_ctime_ns` and DEC-763 preserves metadata changes across two snapshots. However, synthetic fstat objects could still inject arbitrary-precision Python integers far beyond Linux's signed 64-bit timespec seconds plus bounded nanosecond fraction, potentially making a forged timestamp pair appear coherent.

DEC-766 defines conservative Linux timespec-derived nanosecond limits from `-2^63 * 10^9` through `2^63 * 10^9 - 1` inclusive. Both exact plain integer timestamp fields must lie within that range before reads or comparisons. The existing regular-file/device/inode/size/mode validation and outward snapshot API remain unchanged. Three source-defined methods bring the suite to **359 uniquely named tests**: injected out-of-range mtime/ctime values fail before read and close a valid FD, both extreme representable bounds remain allowed, and negative pre-epoch timestamps are preserved.

This is a bounded local synthetic fstat input contract, not independently verified kernel clocks, OS-enforced no-write protection or annual-runner authorization.

## DEC-767 — Reject oversized names before filesystem encoding and malformed encoder returns

DEC-764 adds a shared scanner/evaluator basename predicate requiring a valid Linux single-component filename of at most 255 encoded bytes. The helper initially called `os.fsencode` before checking the length. A synthetic plain string with an arbitrarily large character count could therefore force an unnecessary proportional-size encoding allocation even though it was already impossible to represent as a Linux basename. A patched encoder returning a nonbytes or bytes subclass could also reach subsequent comparisons and formatting.

DEC-767 checks the exact string's codepoint length `1..255` **before encoding**, then requires an exact immutable `bytes` result from `os.fsencode` before checking encoded-byte length and forbidden separators. Real Linux filenames and surrogateescaped byte names retain their accepted behavior. Three new source-defined tests bring the suite to **362 unique test methods**: overlong injected names never invoke the encoder, patched nonbytes/hostile-subclass encoder results cannot pass, and an injected encoder exception cannot create a quiet evaluator result. It still enumerates at most three directory entries, and all receipts remain nonauthorizing.

## DEC-768 — Emit a fail-closed JSON receipt for invalid synthetic observer CLI arguments

The disposable observer's own program entry point prints a nonauthorizing JSON receipt for a missing opt-in or any completed `run_demo` outcome. However, `argparse` previously raised `SystemExit(2)` for unexpected flags, forbidden caller-supplied file paths or mutually exclusive negative-control modes **before** a receipt was emitted. These already failed closed at the shell exit-status level, but left no machine-readable status for the caller to distinguish from unrelated stderr failures.

DEC-768 catches `SystemExit` **only around `parse_args`** and emits the standard `BLOCKED`, exit-2, hardcoded no-dispatch/no-independent-proof JSON receipt. The normal parser still emits usage diagnostics on stderr; supported explicit opt-ins and missing-opt-in behavior are unchanged. The generated filesystem operation is never invoked for invalid CLI arguments. Three new subprocess-based source-defined regression methods bring the suite to **365 unique tests**: forbidden `--source` path, conflicting negative switches, and unsupported help switch all return blocked JSON and never authorize. This change does not authorize caller-controlled inputs or production behavior.

## DEC-769 — Reject reversed directions for one observed rename cookie

DEC-761 rejects repeated `IN_MOVED_FROM` or repeated `IN_MOVED_TO` records with one nonzero rename cookie. It still admitted a synthetic stream where the `IN_MOVED_TO` for a cookie appeared **before** the `IN_MOVED_FROM` for the same cookie, even though Linux emits the FROM event first. The pair does not have to be adjacent in the inotify queue, but reversed order does not represent the normal kernel rename sequence.

DEC-769 records both direction and prior seen action, rejecting an observed `IN_MOVED_FROM` if the same cookie already appeared on a `IN_MOVED_TO`. It keeps unpaired directions with different cookies legal because the other rename endpoint may be outside the watched directory. It also keeps correctly ordered matching-cookie pairs with unrelated interleaved events legal. Three source-defined tests increase the suite to **368 uniquely named test methods**: reversed same-cookie pairs fail, different-cookie unpaired events remain syntactically acceptable, and a nonadjacent correctly ordered pair stays acceptable. None of these local synthetic records authenticate the actual kernel stream or annual host permissions.

## DEC-770 — Require consistent file-versus-directory kind in one rename-cookie pair

DEC-761 and DEC-769 refuse duplicate and reversed rename directions, respectively. The decoder previously still accepted a synthetic pair bearing one cookie where the `IN_MOVED_FROM` side described a regular file and the `IN_MOVED_TO` side carried `IN_ISDIR`, or vice versa. A rename of one inode cannot change that inode's file type, so such a pair does not describe a coherent observed kernel rename.

DEC-770 records the `IN_ISDIR` modifier for each observed nonzero rename cookie and refuses a later same-cookie event whose directory/file kind disagrees. Matching file/file and directory/directory pairs remain well-formed, as do unmatched one-sided rename events when the other endpoint is outside the monitored directory. Four new source-defined methods bring the suite to **372 uniquely named test methods**, checking both incompatible directions and both consistent controls. This uses only already bounded event records and never claims independent kernel provenance, actual OS write prevention, or annual-runner authorization.

## DEC-771 — Bounded cross-product tests for rename-cookie grammar and nonauthorization

The previous drafts DEC-759, DEC-761, DEC-769 and DEC-770 added independent rules for zero rename cookies, repeated direction, FROM-before-TO order, and file/directory-kind consistency. DEC-771 is a **test-only child** that checks these rule interactions without expanding production parser behavior. It exhaustively checks 48 two-event combinations: zero/nonzero/max-uint32 cookies, file/directory kind on both endpoints, reversed/nonreversed order, and presence/absence of an unrelated interleaved file attribute event. Only nonzero, ordered, equal-kind paired moves may be declared syntactically well-formed; every synthetic directory mutation remains `BLOCKED` and nonauthorizing.

Additional methods check that 128 distinct unpaired move-from cookies still fit within the 65,536-byte event bound and parse while yielding a blocked receipt, and that a duplicate cookie direction separated by 64 unrelated cookie records remains malformed. Three source-defined methods bring the suite to **375 uniquely named tests**. The only changed files in this child are the disposable observer test module and documentation. These synthetic cases do not establish independent kernel provenance, OS isolation or annual run385 eligibility.

## DEC-772 — Reject impossible reserved bits in synthetic Linux regular-file modes

DEC-760 bounds synthetic `st_mode` to unsigned 32-bit Linux `mode_t`, and DEC-763 compares both checked modes before/after the snapshot read. However, that width bound still permitted arbitrary *reserved high bits within 32 bits*, because Python's `stat.S_ISREG` tests only masked low file-type bits. A fabricated mode such as `0x10000 | S_IFREG | 0600` could pass as a plausible regular file.

DEC-772 requires `st_mode & ~0o177777 == 0` before the regular-file test. Standard Linux file-type bits (`0o170000`) and all permission/setuid/setgid/sticky bits (`0o7777`) remain available. Two new regression methods bring the suite to **377 uniquely named methods**: several reserved high bits must fail before `os.read` with valid snapshot FD cleanup, and full legal special permission bits remain accepted. This is a conservative synthetic metadata shape check; it neither authenticates kernel snapshots nor proves OS-enforced annual host write prevention.

## DEC-773 — Require exactly one hard link for generated regular sample snapshots

The disposable observer snapshots a generated `/tmp` regular file and monitors its file WD plus the generated directory WD. The earlier `fstat` checker validated mode, device, inode, size and times but not `st_nlink`: an injected fake object could claim a clean sample even with `st_nlink=0` (already unlinked) or multiple hard links, potentially exposing another path to the same inode outside the observed directory. Neither state matches the generated single-file fixture.

DEC-773 requires a plain integer `st_nlink==1` in **both fstat checks**, before any read, while retaining the existing six-part internal comparison tuple and outward `((dev, ino), bytes)` snapshot contract. The synthetic test fixtures now include one-link metadata consistently; they are not kernel-sourced proof. Three new source-defined tests bring the suite to **380 uniquely named methods**: reject zero/multiple/negative/out-of-range link counts before reads and close the acquired FD, reject forged bool/float/string/int-subclass counts, and preserve the one-link metadata tuple. Kernel link counts can change between reads; passing snapshots do not prove absence of adversarial races or independent OS write protection.

## DEC-774 — Live generated /tmp hard-link and unlink controls for the one-link guard

DEC-773 adds an exact `st_nlink == 1` check at both synthetic bounded `fstat` observation points. DEC-774 is a **test-and-doc-only strict child** that exercises the same logic with real disposable Linux kernel link-count transitions rather than just patched fstat objects. It creates new public bytes in a private `/tmp` directory, proves a baseline snapshot works, adds a second hard link in that same disposable folder, verifies `st_nlink=2` and snapshot refusal, removes the alias, then verifies the original snapshot succeeds again at `st_nlink=1`. A separate generated-file test opens a disposable FD, unlinks its pathname, verifies a real `fstat` returns `st_nlink=0`, and checks the metadata helper refuses it. Both tests close their own handles and clean up through `TemporaryDirectory`.

Two live-Linux source-defined tests bring the suite to **382 uniquely named methods**. No source runtime changes, no protected annual source/evidence, no production runner access and no inference that local hard-link refusal enforces OS confinement. This is a real-kernel toy regression, not an independently qualified security review.

## DEC-775 — Explicit generated hard-link alias negative mode (always blocked)

DEC-773 checks `st_nlink==1`, and DEC-774 validates refusal on real disposable `/tmp` hard-link and unlink transitions. DEC-775 makes this visible as a **new opt-in negative control**: `--execute-hardlink-alias-negative`. After starting both normal inotify watches and checking the generated public `BEFORE` fixture, the mode creates a second hard link to the **same generated inode in the same private `/tmp` directory**. It then attempts a guarded snapshot: an `OSError` is recorded as a deliberately blocked negative control, while a mocked snapshot that incorrectly accepts the aliased inode is **also** returned as `BLOCKED` with an explicit failure finding. In either branch, the inotify FD closes in the existing `finally` and the generated directory and alias are cleaned by `TemporaryDirectory`. No automatic or annual runner invocation is added.

The new mode is mutually exclusive with the other negative controls at both `run_demo` and CLI boundaries, and never feeds a hard-link fixture into the evaluator as purported quiet evidence. Four source-defined regression methods increase the suite to **386 uniquely named methods**: malformed mode type fails before watch allocation, mixing this mode with existing negatives is rejected, an injected snapshot bypass is still blocked with FD cleanup, and explicit CLI usage yields `BLOCKED` exit2 with false authorization flags. This is an untrusted *local* filesystem demonstration, not security proof of protected annual job confinement.

## DEC-776 — Verify the new hard-link CLI control executes and fails closed

DEC-775 adds `--execute-hardlink-alias-negative`, an explicit generated `/tmp` negative mode that always blocks regardless of whether the single-link snapshot guard refuses or an injected helper wrongly accepts the alias. DEC-776 is a **test-and-documentation-only strict child** strengthening control-path verification: a live Linux inotify/watch experiment must reach the specific negative-control refusal finding after creating the generated link alias; a patched `os.link` wrapper that raises unexpectedly must produce `BLOCKED` and close the valid observer FD without draining a fabricated queue; and conflicting CLI opt-ins must return nonauthorizing exit-2 JSON without launching the runner.

Three source-defined methods bring the suite to **389 uniquely named tests**. No production runtime, script source, workflow, runner, permission or protected annual evidence is changed in this child. A correctly observed local refusal remains *toy negative evidence*, not independent OS-enforced isolation or annual 385 admission.

## DEC-777 — Check and retain Linux snapshot ownership metadata

DEC-773 requires a singly linked disposable sample, but previous fstat snapshot equality omitted `st_uid` and `st_gid`. This could let an injected metadata pair with changed owner/group IDs but forged identical timestamps pass as stable. DEC-777 requires exact plain integers within Linux's unsigned 32-bit uid_t/gid_t range and appends both to the compared metadata tuple, without shifting the existing mode, dev, ino, size or timestamp positions or changing the public `((dev, ino), bytes)` snapshot result.

All synthetic fstat fixtures supply valid `st_uid=0`, `st_gid=0` fields rather than failing for missing attributes; their direct metadata return assertions are adjusted to the new eight-field tuple. Three new source-defined regression methods increase the suite to **392 uniquely named tests**: owner/group drift with otherwise constant metadata is rejected with FD cleanup, malformed/oversized/hostile owner IDs fail closed, and legitimate UINT32 boundary IDs remain supported. This does not prove independent Linux host identity attestation or annual OS write-prevention.

## DEC-778 — Bounded snapshot metadata drift matrix and live Linux owner IDs

DEC-747–777 now check the disposable snapshot's stat mode, device, inode, one-link count, size, timestamps, UID and GID. DEC-778 is a **test-only** regression child that verifies these checks continue to work together and preserve the stable outward snapshot identity. An eight-case fstat before/after matrix changes **exactly one admissible field** at a time (mode, dev, inode, size, mtime_ns, ctime_ns, uid or gid), leaving the remaining metadata and file content constant, and requires each drift to become an `OSError` with exactly one FD close. A matching eight-field control still returns the original `((dev, ino), bytes)` snapshot. A live generated `/tmp` file test confirms kernel-provided `st_uid`/`st_gid` appear in the checked tuple and that a one-linked public file can still be read.

Three new source-defined methods increase the suite to **395 uniquely named methods**. Only synthetic test code and documentation change; no watcher source logic or annual permissions. These adversarial local regression cases do not authenticate kernel origin independently or establish host OS write denial.

## DEC-779 — Verify generated hard-link negative-control alias before claiming a refusal

DEC-775 makes a deliberately `BLOCKED` hard-link negative control available through an explicit CLI flag. Its first version called `os.link` and attempted a rejecting snapshot, but a patched link wrapper could return success without creating any alias. A later unrelated snapshot error might then be misdescribed as detection of a real two-linked inode.

DEC-779 adds `_plausible_generated_hardlink_pair`, a fail-closed **same-process local** check after creating the public alias but before attempting its guarded snapshot. It uses no-follow `os.stat` on the source and alias, requires exact ordinary integer mode/device/inode/link-count fields, both regular-file modes with no forbidden high bits, bounded identity values, exactly two hard links on each path, and identical `(mode, device, inode, nlink)` tuples. Missing or malformed values become an explicit `BLOCKED` alias-unverified finding; they never contribute to a claimed guard detection. This is not independent verification of kernel or annual host permissions.

Four source-defined tests increase the suite to **399 uniquely named methods**, covering mismatched/injected stat identities, missing aliases, an inert mocked link syscall that returns normally without creating an alias (while still cleaning up the watcher FD), and a live disposable Linux link/unlink identity cycle. Only the generated /tmp observer source, synthetic tests, and documentation change.

## DEC-780 — Require the native nonvoid-status contract for generated os.link

DEC-779 verifies that the generated public hard-link negative control actually produced two paths referring to one inode with kernel-reported link counts of two. The control still ignored the direct `os.link` return, however. Python's successful `os.link` has a **void (`None`) result**; a patched wrapper returning a truthy or other nonvoid value is not a reliable successful syscall result and must not reach the later control-verification boundary.

DEC-780 validates `linked is None` immediately after the generated-link attempt, returning an explicit `BLOCKED` malformed-status finding if the shape is not exact, before any alias verification or second snapshot. Two new source-defined regression methods raise the suite to **401 distinct test methods**: hostile nonvoid returns are rejected with valid observer FD cleanup and no alias-verifier invocation, while a live disposable Linux `os.link` returns native `None` and the resulting two-link alias remains locally verifiable. This only hardens same-process disposable API contracts; neither syscall return nor local /tmp stat values provide independently authenticated host security proof.

## DEC-781 — Attribute hard-link negative refusal only to its one-link guard

The generated /tmp alias negative mode previously interpreted *any* `OSError` from the second bounded snapshot as proof that the one-link guard rejected a two-linked inode. An injected read error, unrelated open/fstat failure or wrapper exception could therefore be credited as a detected hard-link negative even after locally verifying the alias path. Such a receipt was still `BLOCKED`, but misrepresented the provenance of its detection.

DEC-781 introduces a narrow `_SnapshotHardlinkCountError(OSError)` emitted **only** when valid ordinary snapshot metadata has a link count other than one. The alias negative mode credits only this precise subtype; other snapshot `OSError` exceptions are still `BLOCKED` but carry a separate 'without link-count proof' finding. This preserves every existing fail-closed result and the outward snapshot bytes/identity interface. The internal checked-metadata return annotation is also brought into line with its existing eight-field tuple.

Three source-defined regression methods bring the suite to **404 distinct methods**, testing the specific subtype, refusal to credit a synthetic unrelated OSError and successful classification of the precise one-link guard. No production annual runner or protected data is touched; even a locally credited control is not independent OS confinement proof.

## DEC-782 — Compare bounded alias metadata beyond the inode number

The generated public hard-link alias verifier already required two no-follow path stats to match on regular-file type, mode, device, inode and a two-link count. It did not compare bounded UID/GID, file size or nanosecond timestamps. Two stat records for the *same inode* that disagree on these fields signal an inconsistent or racing observation, not a stable local two-link witness. DEC-782 validates those fields as exact native-width plain integers, enforces the existing snapshot UID/GID, size and timestamp ranges, and requires equality across both paths, while keeping the alias negative mode permanently BLOCKED. Existing synthetic stat fixtures are expanded with valid fields.

Two new regression methods bring the suite to **406 unique test methods**: inconsistent owner/group/size/time values invalidate an otherwise matching device/inode pair; malformed, impossible or substituted values are rejected before crediting local alias identity. Real generated /tmp hard-link tests remain unchanged. This strengthens only local disposable consistency and does not prove independent kernel-origin evidence or production annual OS confinement.

## DEC-783 — Revalidate the generated two-link alias after the link-count refusal

DEC-781 distinguishes the precise `_SnapshotHardlinkCountError` from unrelated snapshot errors, and DEC-782 checks bounded metadata from both alias path stats. The hard-link negative mode still credited a specific link-count refusal based only on an alias check **before** the second snapshot. If the generated two-link alias disappeared or its identity changed during the probe, the successful local witness claim would be stale, even though the final status remained BLOCKED.

DEC-783 performs the same bounded no-follow generated-path alias check a **second time after catching the precise link-count refusal**. Only two successful verifications bracketing the refusal may receive its local 'negative control blocked' finding. If the post-check fails, the status stays BLOCKED but reports 'alias changed during guard probe'. Two new source-defined regression methods bring the suite to **408 distinct test methods**: alias loss is not credited even with the precise exception and valid watch cleanup, and matching before/after alias checks retain the expected negative-control finding. This does not close an adversarial race between two observations or constitute independent OS enforcement.

## DEC-784 — Require the exact generated public sample size in hard-link alias checks

The local alias verifier already compares two matching, bounded inode metadata records and DEC-783 rechecks them around the link-count refusal. Those checks still accepted any size between 0 and 4096 bytes. A test wrapper could therefore claim a stable two-linked *different-sized* fixture despite the mode having generated exactly `BEFORE` bytes and verified them at the initial snapshot.

DEC-784 requires each local alias stat to report `st_size == len(BEFORE)` as part of the existing bounded identity predicate, ensuring later alias checks still refer to a fixture of the expected byte length. Source comparisons remain conservative and the mode always returns BLOCKED; byte-length consistency is not content authentication or race freedom. Mocked alias stat fixtures are updated from arbitrary sizes to the actual public fixture length. Two source-defined regression methods raise the suite to **410 unique methods**: two agreeing forged stats with the wrong length must fail and a generated native Linux alias is accepted at the proper length but rejected after writing extra bytes. Only the disposable observer, tests and docs change.

## DEC-785 — Bind generated alias verification to the watched baseline device/inode

DEC-779–784 validate the two local generated pathname stats, their bounded metadata, their recheck after link-count refusal and the fixed public fixture size. They did not compare the two-linked inode against **the original device/inode identity captured immediately after both inotify watches were installed**. An external pathname replacement or injected baseline identity could therefore make two new paths agree with each other while not referring to the actual watched baseline inode.

DEC-785 adds an optional `expected_inode=(dev, ino)` comparison to the reusable alias consistency helper, checking its exact plain integer pair and UINT64 bounds. The hard-link negative mode supplies `original_inode` to **both** checks, before and after the guarded snapshot. Disagreement becomes `BLOCKED` alias-unverified rather than a credited local detection. Direct helper calls without expected identity remain useful in independent generated-file tests, but cannot replace the mode's pinned identity. Two new regression methods raise the suite to **412 uniquely named methods**: mock alias records agreeing with each other but disagreeing with the baseline are rejected; an actual generated alias cannot pass an injected wrong baseline identity. The earlier synthetic bypass test now explicitly stubs alias verification so it continues to test only the no-authorization result of an accepting snapshot helper.

This remains a same-process disposable /tmp consistency check with no independent trusted kernel provenance, race freedom or annual run385 host confinement proof.

## DEC-786 — Live generated pathname replacement negative test for baseline inode pinning

DEC-785 binds both generated hard-link alias checks to the exact `(st_dev, st_ino)` from the initial watched public-file snapshot. DEC-786 is a **test-and-doc-only** child validating this with real disposable Linux inode changes. It creates an original public `/tmp` sample, stores its device/inode pair, separately creates a same-byte replacement inode, replaces the sample pathname, then creates a second link to the replacement. The two new paths correctly agree with each other but the pinned baseline verifier must reject them. A matching control keeps the original generated inode, proves the pinned alias check works with a real two-link pair, then removes the alias and verifies refusal. Both tests create and remove only new public private `/tmp` files.

Two source-defined live methods raise the suite to **414 uniquely named tests**. No runtime observer source, protected data or production workflow changes. Correct behavior remains local negative evidence, not a trusted observer, OS confinement or annual run authorization.

## DEC-787 — Single-field alias consistency matrix and pre-stat baseline validation

DEC-782–786 require the two generated alias path stats to match on mode, device, inode, link count, owner/group, exact generated byte length and nanosecond timestamps, and to match the inode captured before the link operation. DEC-787 is a **test-only strict child** ensuring these independent invariants cannot be accidentally removed by a future edit. It modifies one of the nine stat fields in exactly one of the two alias records over 18 bounded cases, requiring every inconsistent pair to fail; a fully matching control remains true. A separate method feeds ten malformed baseline identity shapes, ensuring the strict tuple and integer validation refuses them **before** any `os.stat` call.

Two new source-defined methods bring the suite to **416 unique tests**. Only disposable observer tests and documentation are changed. The synthetic matrix is not host OS-enforced write denial, independently authenticated kernel provenance or annual run385 authorization.

## DEC-788 — Native link and alias-stat failure cleanup regression coverage

The explicit generated hard-link negative control now checks the void `os.link` return, verifies both bounded alias records match the watched baseline, credits only the precise link-count refusal and rechecks the alias afterward. DEC-788 is a **test-and-doc-only** child proving native-style syscall failures never get miscredited as a successful local link guard and never leak the allocated watcher.

Three native `OSError` subclasses (`PermissionError`, `FileExistsError` and another link failure) must stop before the alias verifier or second snapshot, return a nonauthorizing `BLOCKED` receipt, and close the observer FD. A separate injected `FileNotFoundError` when statting an allegedly linked alias must return a specific `BLOCKED` alias-unverified result with the FD closed and no credited link-count detection. Two new source-defined methods raise the suite to **418 unique tests**. No runtime observer script is modified by this child, and no generated local proof is annual OS isolation authorization.

## DEC-789 — Narrow synthetic os.stat failure to the generated alias pathname

The historical full `tests` run for DEC-788 draft #959 at exact SHA `015480a4427a2bda84032e1a98eef6b2ad9cf21f` **FAILED**, despite its green Phase 3 check. GitHub Actions `unit-tests` job 114355546896 reported 5319 tests run, one failure: `test_hardlink_alias_stat_failure_cannot_credit_detection_or_leak_fd` expected the alias-unverified finding but received `Linux disposable kernel event monitor unavailable`. The test patched the shared `os.stat` object to always raise `FileNotFoundError`; Python `os.path.isdir("/tmp")` also calls this same function, causing the runtime environment preflight to block *before* the deliberately missing alias was reached.

DEC-789 **does not alter runtime source**. It captures the native `os.stat` before patching and delegates all checks except the one synthetic `public-hardlink-alias` basename, for which it raises the requested missing-alias error. The repaired regression asserts the specific alias pathname was actually queried, that the result is BLOCKED for alias-unverified rather than monitor-unavailable, and that the watcher FD closes. A second regression verifies both `/tmp` preflight and the intended missing-alias query occur in one run. Two source-defined methods are now added since #958, bringing the suite to **419 unique methods** (one original failing method repaired, one added). This is a narrow mock-hygiene fix following a **real red historical CI conclusion**; #959 remains red at its recorded SHA and is not retroactively relabeled.

The child remains an unmerged, nonauthorizing local generated /tmp witness; a full historical CI success and independent qualified source/security review are still needed at its own exact head. DEC-650 real OS confinement and DEC-651 immutable one-shot annual admission remain BLOCKED.

## DEC-790 — Verify no-follow alias lookup rejects a generated symlink

The generated public hard-link negative control is meant to prove two directory entries identify the same watched inode and that a bounded snapshot refuses a link count greater than one. The alias verifier uses `os.stat(..., follow_symlinks=False)` for both paths. A symbolic link to the sample is **not** a second hard link, and must not be mistaken for one even though it resolves to the same content if followed.

DEC-790 adds a test-and-documentation-only child: a live generated /tmp symlink to the sample must be refused by the pinned alias verifier, while replacing it with a genuine second hard link must be accepted as **only a local same-process identity check**. A synthetic two-path test asserts the verifier passes `follow_symlinks=False` for both stat calls, preventing accidental relaxation. This adds **two source-defined regression methods (421 total distinct tests)**. The observer source itself and annual runner remain unchanged; local tests do not prove independent OS enforcement or permit run385 admission.

## DEC-791 — Constrain generated inotify watch target kinds at registration

Linux `inotify_add_watch` normally follows a symlink pathname when installing a watch. The observer snapshots its generated public file with `O_NOFOLLOW`, but watch registration had no matching no-follow guarantee. DEC-791 adds Linux `IN_DONT_FOLLOW` (**0x02000000**) to both registrations, and `IN_ONLYDIR` (**0x01000000**) to the generated parent-directory watch. The kernel is thus asked to watch the supplied path itself rather than follow a symlink, and to refuse a directory watch target that is not a directory. Neither option supplies race-free path pinning, independent OS confinement or protected annual eligibility.

Both bits are **registration options only** and are intentionally excluded from `EVENT_ALLOWED` in the inotify event decoder. The preexisting `MASK` and `DIRECTORY_MASK` event action sets are unchanged. Two added source-defined methods increase the test suite to **423 uniquely named methods**: an injected libc wrapper verifies exact safe registration masks for both generated pathnames, and synthetic event records bearing either registration-only bit are rejected. Linux reference: https://man7.org/linux/man-pages/man7/inotify.7.html . Runtime still always refuses annual authorization and only accesses generated /tmp fixtures in tests.

## DEC-792 — Validate exact bounded C pathnames before generated watch registration

The disposable observer registers both watches using `ctypes` `inotify_add_watch` with a `char *` pathname. Although actual public sample names come from `TemporaryDirectory`, an injected or patched `os.fsencode` result could substitute unrelated pathname bytes or contain an embedded NUL. A C pathname truncates at NUL, so merely assuming the wrapper returned the intended path is not fail-closed.

DEC-792 introduces `_checked_watch_path_bytes` for both generated file and parent-directory registrations, requiring an exact plain Python `str` path, exact immutable `bytes` encoding equal to the path encoded with the active Python filesystem encoding and surrogateescape error handler, a nonempty path of at most 4095 bytes, and no NUL. An unexpected encoder exception becomes a controlled `OSError`; after the watcher fd has been created, existing setup cleanup closes it on rejection. Existing `IN_DONT_FOLLOW` and `IN_ONLYDIR` registration flags remain intact. Three new source-defined tests increase the suite to **426 uniquely named methods**, including forged bytes, a correct surrogateescaped Linux filename, and allocated watch FD cleanup before libc registration on a substituted path.

This is input-contract hardening of the generated toy observer, not independent pathname race exclusion, real annual OS write denial or permission to dispatch run385.

## DEC-793 — Live generated Linux controls for no-follow watch registration

DEC-791 adds `IN_DONT_FOLLOW` on both registrations and `IN_ONLYDIR` on the generated parent directory. DEC-792 checks the exact pathname bytes before handing them to `ctypes`. DEC-793 is a **test-and-doc-only strict child** exercising these safeguards on genuine Linux kernel watch registrations using newly generated public files inside a private `/tmp` folder. A positive control creates a regular sample, registers both watches and confirms distinct positive WDs and the unchanged regular-file snapshot. A negative control creates a symbolic-link pathname inside the same generated folder, registers it with no-follow semantics, and checks that a bounded regular-file snapshot of the symlink fails via `O_NOFOLLOW`. Both controls close their inotify FDs and remove only their own generated fixtures. The tests are skipped on non-Linux systems.

These checks add **two source-defined test methods (428 total unique methods)** and do not modify the observer runtime or production runner. They are not independently authenticated kernel provenance, race-free watch registration or annual OS confinement proof.

## DEC-794 — Enforce lexical /tmp scope before encoding generated watch paths

DEC-792 checks that `inotify_add_watch` receives the same exact bounded NUL-free bytes as its Python pathname. Correctly encoded bytes can nevertheless designate an unintended path such as `/etc/passwd`, a relative pathname resolving against an unrelated current directory, or a `/tmp/../` traversal. The disposable helper should never opt in to watch those explicit caller-selected targets. DEC-794 requires its pathname be exactly `/tmp` (for direct synthetic one-child cases) or begin with `/tmp/`, rejects any `..` path component, and refuses non-string path representations **before invoking `os.fsencode`**. Both generated file and directory registrations already use this shared helper; no new run mode or arbitrary source input is added.

Two added source-defined tests bring the suite to **430 uniquely named methods**: invalid outside/relative/traversal paths fail *before* encoding, while the generated public /tmp root and representative private children still yield unchanged bytes. This is a **lexical scope boundary**, not a proof against malicious intermediate symlink substitution, a race-free directory-fd confinement mechanism or annual host OS write-denial. Only generated observer source, tests and docs change; all authorization flags remain false.

## DEC-795 — Bind path-like text to the generated Path object itself

DEC-792 rejects C watch pathname bytes that differ from `os.fspath(path)`; DEC-794 enforces a lexical absolute /tmp scope. An injected pair of Python wrappers could nevertheless return a **different** /tmp path from `os.fspath(path)` and matching forged bytes from `os.fsencode(path)`. That would appear internally coherent even though the original generated Path object still identifies another file.

DEC-795 checks that the exact plain string from `os.fspath(path)` equals `str(path)`, the generated `Path` object's own textual representation, **before** encoding. A substitution becomes a handled `OSError` and watch setup closes any already allocated nonstdio inotify FD. This is not a kernel race-free pathname guarantee; it only prevents the tested Python-wrapper mismatch. Two new source-defined tests increase the suite to **432 uniquely named methods**, covering substituted in-scope and out-of-scope `fspath` strings without calling the encoder, and a normal absolute generated public Path. Only disposable observer source, tests and docs change.

## DEC-796 — Refuse custom pathname objects at generated watch registration

The disposable runner constructs an ordinary `pathlib.Path` for its newly generated public `/tmp` sample, while the watch setup helper accepts a Python Path argument. DEC-792–795 check its encoded C bytes, lexical scope, and `os.fspath` consistency, but a synthetic caller can supply a custom `Path` subclass with attacker-defined `__fspath__` behavior instead of the expected generated object.

DEC-796 adds an early exact concrete `Path` type check (`type(path) is type(Path())`) **before invoking any filesystem encoder or path-like method**. Malformed subclasses, raw strings, raw bytes and other Python objects fail with handled OSError, while the normal generated Path still encodes unchanged. Two new source-defined tests bring the suite to **434 unique test methods**. This is generated observer API shape validation, not host-independent security isolation, protection against mutable intermediate symlinks or annual runner authorization.

## DEC-797 — Handle unexpected /tmp environment probe errors before mutation

The generated Linux /tmp observer previously checked `os.path.isdir("/tmp")` and `os.path.islink("/tmp")` **outside** its general error boundary. A patched or unexpectedly failing Python probe could therefore raise a `RuntimeError` before the script emitted its permanently nonauthorizing JSON receipt. Worse, injected truthy and falsy non-boolean results could be treated like real filesystem assertions.

DEC-797 isolates the Linux platform gate, wraps both /tmp probes in a narrow ordinary `Exception` handler, and requires exact identity `is True` for directory status and `is False` for symlink status. Any exception or malformed injected result returns the same `BLOCKED` monitor-unavailable finding **before creating any public files or starting any watches**. The existing disposable setup, cleanup and no-authorization semantics remain unchanged. Two source-defined tests bring the suite to **436 uniquely named methods**, covering exceptions from each probe and several non-boolean forged values. This is local preflight fault tolerance, not independent host OS enforcement or annual run385 authority.

## DEC-798 — Require exact booleans from generated alias verification

The `run_demo(hardlink_negative=True)` mode already requires a matching baseline-pinned, bounded two-link alias **before** the guard probe and **after** its precise link-count refusal. However, both checks used Python truthiness (`if not helper(...)`), so an injected verification helper returning `1`, a nonempty string, an object, or a hostile `__bool__` implementation could be mistaken for authenticated local verification. A truthy object could also cause an uncontrolled exception instead of the narrow nonauthorizing finding.

DEC-798 makes both calls accept **only literal `True`** (`is not True`); all other return shapes are treated as unverified and `BLOCKED`. The helper itself remains exact-integer checked; the change protects its separate caller boundary from monkeypatched return objects. Two source-defined regression methods grow the suite to **438 unique test methods** and cover six falsy/truthy/malicious return shapes at each boundary, with expected findings, no drain, and valid watcher cleanup. No annual host isolation or dispatch authority is claimed.


## DEC-799 — Refuse synthetic platform spoofing before generated /tmp preflight

DEC-797 restricted the generated /tmp probes to exact booleans, and DEC-798 restricted the two hard-link alias-verifier gates to exact `True`. The Linux platform gate still used `sys.platform != "linux"`; a monkeypatched object with a hostile `__ne__` method could pretend to be Linux and reach those /tmp probes without being a real platform string.

DEC-799 accepts only `type(sys.platform) is str` together with `sys.platform == "linux"` before entering any generated-filesystem preflight. Two source-defined tests bring this descendant to **440 distinct test methods**, checking forged comparison objects, a `str` subclass, non-Linux strings and nonstring stand-ins. Each must return the usual permanently nonauthorizing `BLOCKED` receipt, without even calling `os.path.isdir` or starting inotify. All existing real plain Linux observations remain eligible only for local unverified witness status. This is synthetic Python boundary hardening, not OS attestation, actual 20-job annual isolation or run385 admission.


## DEC-800 — Bind the disposable temporary directory to its generated /tmp scope before writing

The observer calls `tempfile.TemporaryDirectory(prefix=..., dir="/tmp")` and then writes `sample` into the returned path before opening either inotify watch. Normal Python returns a fresh private /tmp folder, but a patched or defective context-manager result could return a different path, including an outside-/tmp directory, and the earlier runtime would attempt a sample write before any watch-path guard could reject it.

DEC-800 introduces a local pre-write validator: the context manager must return a **plain str**, canonical direct child of `/tmp`, with a nonempty `dec677-disposable-` basename suffix and a bounded valid Linux entry name. Only then can the public `sample` path be constructed and its initial bytes written. Two new source-defined regression methods bring the descendant suite to **442 uniquely named tests**. Injected noncanonical/out-of-scope paths, wrong prefixes and nonstring/subclass values must BLOCK with zero sample writes and zero watch starts; a genuinely generated `TemporaryDirectory` remains admissible to the local toy runner. This is lexical Python-wrapper input validation, NOT race-free path containment, OS write isolation or annual dispatch approval.


## DEC-801 — Require inventory encoding to match the exact supplied name

The scanner and direct evaluator already require exact `str` inventory basenames with valid bounded Linux byte shapes. But a synthetic monkeypatch of `os.fsencode` could substitute other well-formed bytes, allowing the original `"sample"` string to pass a scan despite its encoder returning `b"other"`. DEC-801 checks that native encoded bytes match `name.encode(sys.getfilesystemencoding(), "surrogateescape")` exactly; unexpected encoder errors, wrong byte types and substituted byte content fail closed.

Two source-defined regressions grow this strict child to **444 distinct test methods**. An evaluator with substituted inventory-name bytes must report `BLOCKED` instead of endorsing no directory mutations; actual ordinary, 255-byte and surrogateescaped native Linux basenames still pass the helper. The same issue was separately proposed in sibling draft #998 from #995; this strict descendant of #999 carries the fix forward without rewriting that sibling. Only disposable generated /tmp observer source, tests and docs change. This cannot attest independent kernel provenance, race-free confinement or annual authorization.

## DEC-806 — Integrate native encoded inventory scanner regressions on the expanded stack

The expanded parent #1000 already includes DEC-799's plain-Linux platform gate, DEC-800's generated disposable `/tmp` directory confinement, and DEC-801's exact encoding check for each plain inventory basename. A separate test branch #1001 previously added bounded `os.scandir` tests that were not yet part of this expanded parent chain. DEC-806 ports **only those two test methods** into the stronger parent: a patched encoder returning plausible but substituted bytes for `"sample"` must trigger `OSError` at the actual scanner boundary; and a generated Linux `/tmp` file whose name contains native non-UTF-8 bytes must still be returned losslessly using surrogateescape.

The resulting test inventory contains **446 uniquely named methods**. Only the disposable test module and documentation change; the observer implementation on this parent is unchanged, and no runtime authorization is implied. This test consolidation does not merge any PR, alter protected annual inputs, or turn local observations into independent OS write-prevention evidence.

## DEC-807 — No-follow directory inode check before first generated /tmp file write

DEC-800 validates the lexical `/tmp/dec677-disposable-*` shape returned by `TemporaryDirectory`, rejecting path traversal and substituted out-of-scope text **before** writing the sample. Lexical validation alone does not establish that a returned pathname is a *directory inode*: a monkeypatched temporary-directory context could supply a correctly shaped **symlink to another folder**, redirecting the generated first `sample` write through the link.

DEC-807 adds a no-follow `os.lstat` on the exact returned generated folder and requires an exact native integer Linux `S_IFDIR` mode with no reserved high bits. Missing folders, injected lstat exceptions, noninteger/custom mode values, regular files and symlinks return a controlled `BLOCKED` receipt before `Path.write_bytes` or inotify setup. Three new source-defined regression methods raise the suite to **449 distinct tests**: a real disposable Linux symlink sharing the valid generated prefix is rejected while the real generated directory is accepted, malformed/mocked lstat records are rejected, and a runner-level substituted symlink cannot cause a first sample write or watch registration.

This guards a **prewrite local pathname boundary**, not a race-free FD-relative filesystem sandbox, independent annual OS enforcement or permission to dispatch run385.

## DEC-808 — Require owner-matched private generated /tmp directory permissions

DEC-807 adds a no-follow `os.lstat` check that the generated `/tmp/dec677-disposable-*` path is a real directory rather than a symlink, before the first public sample write. That still allowed a substituted *existing but shared directory* to pass, even though Python's `tempfile.TemporaryDirectory` creates a private mode-`0700` directory owned by the effective user.

DEC-808 additionally requires the lstat-verified directory to have exact private permission/special mode bits `0700`, an exact plain `st_uid` within Linux UINT32 bounds equal to the current exact `os.geteuid()`, and fail-closed behavior for malformed owner probe returns. Three new source-defined tests raise the suite to **452 unique test methods**, including real generated Linux chmod transitions (0700 accepted; group/world-accessible or sticky-mode substitutions refused) and forged/foreign UID and euid-wrapper errors. All checks are before the first generated write. They do not remove pathname TOCTOU races or amount to independently enforced annual filesystem sandboxing.


## DEC-809 — Exercise genuine non-UTF-8 scanner filenames

The generated public inventory tests on DEC-806 tested what they called surrogateescaped names using a **doubled backslash** bytes literal, `b'public-\\\\xff-entry'`. That evaluates to printable backslash/x/f/f text rather than a Linux filename containing the raw byte 255. DEC-809 corrects all three affected references in the existing two methods to use `b'public-' + bytes([255]) + b'-entry'`, preserving both the scanner comparison and its native-byte expectation. An additional method proves the byte-for-byte `fsdecode` → `fsencode` roundtrip and rejects a substituted encoding. This is a **test/docs-only** strict child: source runtime unchanged, **453 unique test methods**, and no promotion of local observer evidence.


## DEC-810 — Prove nonprivate tempdirs stop runner before all writes

DEC-808 checks directory owner and mode in the local generated path validator. This child adds a Linux-native runner-level regression: after safely creating a generated `/tmp/dec677-disposable-*` folder, intentionally chmod it to `0755` or `0777`, inject only its return from the context manager, and require the disposable runner to emit `BLOCKED` without either `Path.write_bytes` or `_start_watch`. The test restores `0700` before the original temporary-folder cleanup. Two unrelated synthetic UID tests also gain explicit non-Linux skip guards so they do not rely on `os.geteuid` on unsupported hosts.

This is a test/docs-only strict descendant integrating the separate prior #1007 runner proof after #1008's real non-UTF-8 fixtures; the total rises to **454 unique source-defined methods**. No runtime changes, no independently enforced annual OS confinement, no dispatch authorization.


## DEC-811 — Require plausible Linux device/inode identity before generated writes

The local tempdir prewrite checks now validate no-follow directory type, exact mode 0700 and effective-user ownership. A synthetic `os.lstat` result could still claim those properties with a malformed or impossible `st_dev` / `st_ino` value. This child requires exact plain integer identifiers bounded by the Linux unsigned 64-bit ABI, with a strictly positive inode, and fails closed if metadata is missing or throws. Two new source-defined regressions raise this lineage to **456 unique test methods**, checking malformed synthetic objects and an actual newly generated Linux /tmp inode. The earlier owner-only positive mock now carries valid dev/ino fields so it still tests its stated property.

This integrates the separate sibling #1009 metadata-identity contract on top of #1010's corrected non-UTF-8 fixtures and shared-directory runner test without altering those recorded commits. Only the generated Linux /tmp observer and associated tests/docs change. This is metadata shape validation, not race-free independent OS isolation or annual run385 authority.


## DEC-812 — Bound remaining generated directory group/link metadata

The disposable prewrite directory checks already require no-follow private owner-matched inode metadata with sane device and inode identifiers. The bounded lstat record's group ID and link count were still ignored. DEC-812 rejects malformed or inaccessible `st_gid` and `st_nlink` values before constructing the public source file: group IDs must be exact plain uint32 integers, and link count must be an exact plain positive uint64 integer. A generated Linux directory is accepted with its native values. Two source-defined regressions bring the strict suite to **458 unique test methods**, while prior synthetic positive metadata records receive sane group/link values.

This is synthetic metadata contract hardening, not a separately trusted kernel proof or an OS-enforced annual runner sandbox; all 20 annual jobs and immutable run385 admission still require independent review.


## DEC-813 — Refuse preexisting sample before first generated write

Even a correctly shaped private owner-matched /tmp folder can be a **substituted existing directory** already containing `sample`. The previous `Path.write_bytes(BEFORE)` could overwrite an existing generated public file or follow a planted symlink before either inotify watch was installed. DEC-813 adds a no-follow `os.lstat(sample)` preflight immediately after the generated folder checks: only a native `FileNotFoundError` (missing entry) permits the initial public write; any existing sample or unexpected lstat error fails closed. Two new source-defined methods raise this strict stack to **460 unique tests**, asserting planted file/symlink bytes stay unchanged, no sample writer or watcher runs, and injected stat errors remain blocked.

This carries the independently drafted #1012 negative-control behavior onto the deeper #1013 lineage without rewriting siblings. The lstat check is **not atomic O_EXCL creation**, does not close pathname races, does not prove independently OS-enforced annual isolation and does not authorize run385.


## DEC-814 — Atomically create generated sample exclusively

DEC-813 rejects a preexisting `sample` file/symlink using `os.lstat` before the first write, but an entry could still arrive after that check and be overwritten or followed by ordinary `Path.write_bytes`. DEC-814 changes only the initial generated public sample to `with path.open("xb")`, invoking Linux exclusive create semantics. A late-arriving existing file or symlink at `sample` is rejected atomically at that basename. The buffered writer must report an exact plain integer number of written bytes equal to `len(BEFORE)` before any inotify registration. Existing mock assertions for the first generated write are updated to patch the actual `Path.open` boundary, not obsolete `Path.write_bytes`.

Two new source-defined tests raise the strict lineage to **462 unique methods**: malformed, boolean, short or oversized synthetic exclusive-write results cannot advance; genuine Linux `xb` creation cannot overwrite a preexisting symlink target in a fresh public /tmp folder. This narrows the file-creation race but **does not** defend against parent-directory replacement, mount aliases or grant annual run385 authorization.


## DEC-815 — False-negative prewrite stat still cannot bypass exclusive create

DEC-814 changed the first generated public sample creation to Linux exclusive `Path.open("xb")` after a no-follow absence check. DEC-815 supplies an adversarial real generated /tmp negative: either a planted regular `sample` or a symlink to another public file exists, while a narrowly scoped `os.lstat(sample)` wrapper intentionally lies that the entry is missing. All other metadata probes delegate to the actual native lstat. `run_demo` must still be BLOCKED with no inotify watcher and unchanged bytes, because O_EXCL independently rejects the existing pathname.

This test/docs-only strict child adds one source-defined test (**463 unique methods**) and incorporates the separate #1016 counterexample into #1017's stronger private-directory metadata lineage. No runtime changes; the exclusive basename gate still does not pin the parent directory or provide independently enforced 20-job annual runner security proof.


## DEC-816 — Exclusive creation also refuses hard links and directories

DEC-814 made the first generated `sample` creation exclusive, and DEC-815 demonstrated that a falsely missing prewrite lstat cannot bypass it for regular-file and symlink sample entries. This test-only child extends the native /tmp collision matrix to **an existing hard link** to a separately generated public file and an **existing directory** containing a generated public child. It injects a false `FileNotFoundError` only for the `sample` lstat preflight, then requires a permanent BLOCKED receipt, no watch registration, stable existing target bytes and original hard-link inode / nested child. Linux O_EXCL refuses any occupied basename regardless of its inode type.

One new source-defined test raises the lineage to **464 distinct test methods**. No runtime changes or independent annual OS-write confinement; only generated public fixtures in private /tmp are touched, with exact-head CI and qualified independent security review still outstanding.


## DEC-817 — Bound buffered exclusive-close failures before watcher creation

DEC-814 checks the initial exclusive sample `write` byte count. A complete-looking buffered write may still fail on context manager close/flush, so DEC-817 adds a regression in which the generated sample writer reports exactly `len(BEFORE)` while its `__exit__` raises a synthetic native `OSError`. The runner must produce `BLOCKED` with no watch allocation and false authorization fields. A separate real Linux /tmp control creates the generated sample using `Path.open("xb")`, checks the exact bytes and inode through the bounded no-follow snapshot helper after close, and proves a second exclusive create fails.

Two source-defined tests increase this descendant to **466 unique methods**. Runtime observer code is unchanged; all data are generated public /tmp fixtures, and this is neither parent-directory OS confinement nor annual run385 admission.


## DEC-818 — Refuse invalid initial exclusive file descriptors before any sample write

The disposable observer guards its snapshot and inotify watcher descriptors against inherited stdio FDs 0–2, but the newly exclusive initial `Path.open("xb")` file was not checked at the same boundary. DEC-818 examines `sample.fileno()` before the first generated write; missing/throwing, forged, oversized, negative or stdio-valued descriptors fail closed without calling `sample.write` or allocating inotify watches. The writer context still performs its own cleanup. A native Linux positive control accepts an ordinary nonstdio FD and writes the exact public fixture. Two inherited mocks for malformed write count and close failure now return a valid nonstdio FD so those tests still reach their actual stated boundaries.

Two new source-defined tests increase this descendant to **468 unique methods**. This is a same-process Python-wrapper FD-shape guard, not independent OS confinement, not protection against malicious wrappers closing inherited descriptors, and not annual run385 admission.


## DEC-819 — Repair inherited forged-fspath test fixture after a real full CI failure

The exact full historical `tests` run for draft #1011, source head `323205c15120d34aee3920ab97164dd406dd0973`, **FAILED** (workflow 38133609970, unit-tests job 114452830132): 5,357 tests, one failed assertion, 693 skipped. `test_watch_encoding_rejects_forged_fspath_and_encoder_agreement` expected the `fspath disagrees` guard but hit the deliberately patched `os.fsencode` exception instead, returning `disposable watch pathname encoding failed`. The inherited test constructed a Python `Path` and did not materialize its expected text until after replacing the shared `os.fspath` wrapper. This is a test-fixture order dependency around lazy path string materialization, not annual-runner authorization.

DEC-819 is test/docs-only: it eagerly captures the unmodified source `Path` text before installing the synthetic `os.fspath` monkeypatch, and asserts the initial value matches the generated public path. The existing regression still requires early fspath mismatch and zero encoder calls. Source runtime code is **identical** to #1021. Distinct source-defined method count remains **468**. #1011's original failed run is not relabeled; this new child requires its own exact-head Phase 3 and full tests.


## DEC-820 — Bind watch-path text to concrete Path parts before synthetic fspath

DEC-819 stabilized an inherited forged-fspath regression after the real #1011 full-history RED result, but the file-watch input validator itself still compared a potentially patched `os.fspath(path)` with `str(path)` after invoking that wrapper. For the generated toy observer, only exact concrete Linux `Path` objects are accepted and every watch must be within `/tmp`. DEC-820 reconstructs an independently expected absolute pathname from the actual concrete `path.parts` tuple **before** invoking `os.fspath`; a different wrapped `fspath` can never supply the watched C string even if an encoder is patched to agree with it. Ordinary `/tmp` paths and their native bytes remain accepted.

One cold-Path regression with no prior string-cache warmup verifies three forged text substitutions are rejected **before** calling the encoder. Total **469 distinct source-defined tests**. This is Python-level path input coherence, not host-independent race-free pathname pinning, OS-enforced annual-job confinement, or authorization. The older #1011 full red log and #1022's separate fixture change remain recorded independently; exact-head Phase 3 and full regression must verify this source-changing child.


## DEC-821 — Initial exclusive writer exception contracts remain fail-closed

DEC-818 requires a plain nonstdio Linux descriptor before writing the initial exclusive public sample. DEC-821 adds two regression methods proving that `sample.fileno()` raising an ordinary `OSError`, unexpected `RuntimeError` or `ValueError` never calls `write` or starts a watcher. A second method provides a valid mocked nonstdio FD but makes the initial `write(BEFORE)` itself raise OSError or RuntimeError; that too must emit a nonauthorizing `BLOCKED` receipt without starting a watch.

This **test/docs-only** strict child carries the two prior sibling #1023 tests into #1025's independently bound watch-path source lineage, without merging or altering sibling commits. It increases the source-defined suite to **471 unique tests**. All results remain only local generated Linux /tmp witness evidence, not an independently enforced annual runner sandbox or dispatch approval.


## DEC-822 — Carry native writer descriptor cleanup into watch-path-guarded lineage

DEC-820 source hardening [#1025](https://github.com/Dtwosam/FMP/pull/1025) independently reconstructs watch text before a forged `os.fspath` call, and DEC-821 [#1026](https://github.com/Dtwosam/FMP/pull/1026) includes two initial writer exception controls. The sibling [#1027](https://github.com/Dtwosam/FMP/pull/1027) explored actual native descriptor cleanup after these errors but did not include #1025's watch-path improvement. DEC-822 ports just those **two native Linux test methods** into the strict #1026 descendant. A real exclusively opened public /tmp sample stream must close after a deliberately thrown `fileno()` failure, `write()` error, or post-close exception. Each condition must also yield `BLOCKED` and zero watch registrations.

The new head has **473 source-defined uniquely named test methods**; only test and docs paths change. The previous sibling PR heads and CI history stay untouched and unmerged. These tests demonstrate local Python context-manager cleanup over public generated data, **not** independently protected annual runner files or immutable server-side annual dispatch. Exact-head Phase 3, full historical regression and qualified independent security review are still required.


## DEC-823 — Verify a newly returned generated private tempdir is empty before first write

Even a correctly shaped owner-matched `0700` generated `/tmp/dec677-disposable-*` directory can be substituted by a defective or adversarial Python `TemporaryDirectory` wrapper after its metadata checks. The runner previously refused an existing `sample` basename through `lstat` plus exclusive `xb` creation, but would still begin writing into an already-populated private folder containing *other* public entries. It detected those extras only at its final inventory.

DEC-823 reuses the existing bounded `_bounded_inventory_names` scanner **before writing any sample bytes**, requiring an exact empty plain tuple and rejecting any existing entry or injected non-tuple/tuple-subclass evidence. This is a bounded, early fail-closed check, not race-free parent pathname pinning or independently enforced filesystem isolation. Two new source-defined tests increase the strict lineage to **475 uniquely named tests**, checking a real generated public sibling remains unchanged with no writer/watch and that forged inventory return types cannot advance. Three inherited negative controls are deliberately preserved: their synthetic inventories are set falsely empty to keep testing the later independent `lstat` and `O_EXCL` collision protections, without renaming historical CI.

Only generated Linux disposable observer source, unit tests and documentation change. Phase 3, full historical CI at this exact source head, and qualified independent security/source review remain necessary. No annual dispatcher permission is introduced.

## DEC-824 — Positive native generated control after prewrite empty-directory enforcement

The new DEC-823 prewrite inventory guard from [#1030](https://github.com/Dtwosam/FMP/pull/1030) refuses any occupied generated /tmp folder before first public sample write. The previously independent sibling [#1031](https://github.com/Dtwosam/FMP/pull/1031) added a mixed native/synthetic positive test to the strict FD-cleanup lineage, but was based on #1029 and did not include this prewrite guard.

DEC-824 ports **one genuine Linux private /tmp positive control** onto #1030 as its strict immediate child. Real tempdir creation, first empty bounded inventory, exclusive sample writing, non-following first/final snapshots and final inventory must still complete; only watch registration and event draining are stubbed, with an ordinary pipe FD that must close. The only acceptable result is `LOCAL_DISPOSABLE_WITNESS_UNVERIFIED` with matching digest/inode checks and both authorization fields false. This proves compatibility of local generated fixtures, **not authentic kernel-event provenance**.

This **test/docs-only** child increases source-defined distinct tests from **475 to 476**, leaving the runtime script and all sibling heads unchanged. All exact-head Phase 3/full historical CI and qualified independent source/security review are mandatory. The old #1003 and #1011 full CI failures remain historically red. Real annual 20-job OS isolation and immutable run385 server dispatch admission remain blocked.

## DEC-825 — Native prewrite success boundary and scanner exception controls

The separate sibling [#1032](https://github.com/Dtwosam/FMP/pull/1032) tests that a truly clean generated Linux private /tmp folder survives the empty-directory check and exclusive initial write before a deliberately stopped watch installation. It also proves that both `OSError` and an unexpected `RuntimeError` from the bounded initial directory census block **before any writer or watcher allocation**. DEC-825 carries these two additional and distinct negative/positive boundary tests onto [#1033](https://github.com/Dtwosam/FMP/pull/1033), which has the full local positive path with a synthetic watcher. No previously created sibling or failed ancestor commits are modified.

With two new source-defined tests, this branch contains **478 uniquely named methods**. The native control asserts actual public sample bytes, pathname scope and cleanup; scanner faults require `BLOCKED`, no sample open and no watch. **Test/docs only**. This does not authenticate kernel events, independently sandbox the protected annual 20 jobs, or authorize annual run385. Exact-head Phase 3, full historical suite and independent security/source review remain mandatory.

## DEC-826 — Native prewatch symlink substitution and link-count refusal

The disposable toy runner validates that the generated private `/tmp` folder is initially empty, exclusively opens the fixed `sample` basename, and checks that watcher setup precedes the first full inode/byte snapshot. There is still a real mutation window **after that exclusive writer closes but before watcher registration**. DEC-826 adds two native Linux boundary controls by instrumenting only the `_start_watch` call site: immediately before reporting mock watch IDs, replace the just-created public sample with a symlink to an identical generated public file, or create an alias hard link of that same inode. The first must fail the subsequent `O_NOFOLLOW` snapshot, and the second must fail the regular-file snapshot link-count invariant.

Both controls must return `BLOCKED` with permanent false authorization/proof fields, never reach the event drainer, and close the disposable mock watcher pipe FD. These are **two additional source-defined test methods**, bringing the strict #1035 descendant from **478 to 480**. Observer runtime is unchanged, and the test mutates only new public disposable tempdir fixtures. This is a mock watch boundary, **not genuine independent kernel observation**; same-content regular-file replacement before watch remains a provenance limitation. Exact-head Phase 3/full historical CI and qualified independent OS/source review remain mandatory, and neither native control authorizes annual run385.

## DEC-827 — Bind the exclusively created public sample inode to watched pathname

Until DEC-827 the local runner verified that an initial `sample` was created exclusively, then waited until after inotify watch registration to take its first no-follow regular-file snapshot. A *different regular inode with the identical public `BEFORE` bytes*, atomically substituted between those stages, could therefore pass the local quiet checks without proving continuity with the originally generated inode. DEC-827 records a bounded plain `(st_dev, st_ino)` identity using `os.fstat` on the real exclusive writer FD while it is still open, and compares it with a bounded `os.lstat` on the target pathname **after both watches have registered, before the first full baseline snapshot**. Unreadable, forged, symlinked or multiply linked file metadata and mismatched identities fail closed to `BLOCKED` and close the watch FD.

Two regression methods bring the strict chain from **480 to 482**: a real native /tmp identical-content inode substitution injected at the registration boundary must be blocked without an event drain, and an invalid-stat-field matrix rejects forged identity objects before comparison. This strengthens an otherwise misleading local provenance claim; it does **not** eliminate the race between pathname validation and snapshot, prevent attacker-controlled parent-directory substitution, prove complete inotify observation, independently enforce no-write OS confinement, or authorize run385. Both exact-head Phase 3 and full historical CI and qualified review are required.

## DEC-828 — Preserve actual close-error boundary after new inode provenance check

DEC-827 now inspects the initial exclusive writer's `os.fstat(fd)` before closing the Python buffered stream. The earlier inherited close-failure test used a fake descriptor `19` without a matching real stat object. Without updating that fixture, the **new fstat check can abort before the intended `__exit__` close-failure injection**, causing a misleading green test that never reaches the claimed boundary.

DEC-828 is a narrow **test/docs-only contract repair**: it supplies a bounded synthetic regular inode record to the fake FD and explicitly requires one `fstat(19)` and a `__exit__(None, None, None)` call (proving the close-error path really ran), while still refusing watch allocation and authorization. One new source-defined test additionally checks that both a native-style `OSError` and an unexpected `RuntimeError` at initial writer `fstat` block and exit the writer context without watch setup. This increases distinct source-defined methods to **483**. Neither #1037's runtime source nor ancestor full/Phase 3 CI is rewritten. This local fake-FD contract is not independent OS proof or run385 admission; new exact-head Phase 3/full CI and qualified security review are mandatory.

## DEC-829 — Repair genuine Python 3.12 cold Path forgery discovered by full CI

Full historical regression at [#1033](https://github.com/Dtwosam/FMP/pull/1033), source `ee9f463c1323fb1ff76a4a81099090f2255fb027`, ran **5,377 tests with three failing subtests and 693 skips**: [workflow 38135600918](https://github.com/Dtwosam/FMP/actions/runs/38135600918), job 114458704724. The cold-path test `test_watch_cold_path_refuses_forged_fspath_before_encoding` requested the early `fspath disagrees` guard. Instead, Python 3.12's lazy `path.parts` parsing consulted globally monkeypatched `os.fspath`, which in one case let execution reach the deliberately disabled encoder and in two other cases raised a scope error too early. This is a real source/test interaction, not evidence of a passing full test.

DEC-829 fixes the **actual watch-path input guard** on a separate strict child of #1038: for an exact concrete CPython `Path`, reconstruct the expected raw pathname from its original **stored list of plain string segments** (`_raw_paths`) using string joins without invoking patched `os.fspath`, `str(path)` or `path.parts`. Any missing/malformed raw segment fails closed. The resulting text must still match the ordinary `os.fspath(path)` output and exact encoded native Linux bytes. This is intentionally limited to generated canonical public /tmp paths and depends on CPython's `pathlib` internals; it does not provide a portable security boundary across Python implementations.

Two new source-defined regressions increase the lineage from **483 to 485**: cold forged wrappers must be refused before the byte encoder, and malformed raw segment storage cannot be credited as an admissible watch path. The original #1033 full historical CI remains **RED** and is not rewritten or relabeled; this new head needs its own Phase 3 and full tests. No protected annual paths or runner settings changed, and the observer still cannot grant annual run385 authorization.

## DEC-830 — Compare the first watched baseline against the original exclusive writer inode

DEC-827 pinned an exact original writer `(st_dev, st_ino)` via native `fstat`, then validated a post-registration `lstat(path)`. There remains a separate same-content **regular inode substitution window between that lstat and the first nofollow source snapshot**. Because the local evaluator compares its first snapshot only to later snapshots, it could otherwise still call this a quiet local witness of an inode that was not exclusively created by this run.

DEC-830 checks the **already validated first nofollow snapshot device/inode** matches the original O_EXCL writer inode as well as the postwatch lstat. A genuinely different regular inode with byte-for-byte matching public `BEFORE` content is now blocked before negative controls, later snapshots or event draining. A native generated Linux regression explicitly swaps the public file only as `_snapshot_regular` begins, preserving its original content bytes, and requires a blocked verdict, one attempted first snapshot, no event drain and a closed mock watcher FD.

One distinct source-defined test raises the strict suite **485→486**. Only the generated disposable observer runtime, its tests and its documentation change. This improves best-effort local provenance but **cannot** prevent a real adversarial rename race, file replacement after the snapshot, mount-namespace substitution, or arbitrary alias writes, and is not authenticated independent OS isolation of all annual jobs or immutable run385 admission. Exact-head Phase 3 + full historical regression and qualified independent security review are still mandatory.

## DEC-831 — Integrate mutating pathname wrapper regression with initial inode baseline pin

A parallel [#1040](https://github.com/Dtwosam/FMP/pull/1040) (strict sibling of #1041, both children of #1039) introduced one useful test of a synthetic `os.fspath` wrapper that not only returns a substituted path but also **mutates the concrete Python Path's underlying constructor segments while being invoked**. The DEC-829 guard must have captured expected watch text before calling that wrapper, and must refuse the substituted target without invoking the byte encoder. DEC-831 ports that exact focused regression into the #1041 strict descendant, which also pins the first watched no-follow inode to the original exclusive writer.

One new source-defined method increases the integrated branch from **486 to 487**. **Test/docs-only**, generated observer runtime unchanged from #1041; #1040's independent sibling head, comments and CI remain intact. The mutation test demonstrates a same-process CPython input-integrity assertion only, not independent kernel/OS filesystem confinement or run385 dispatch authority. This child needs its own Phase 3, full historical tests and qualified review.

## DEC-832 — Real generated inode identity for synthetic snapshot ordering tests

DEC-830 source hardening in [#1041](https://github.com/Dtwosam/FMP/pull/1041) verifies the first watched no-follow snapshot's `(dev, ino)` still matches the initial exclusive writer FD. Before that guard, three synthetic observer ordering tests returned the hard-coded identity `(3,7)` from their fake snapshot despite a genuinely allocated temporary `sample` inode. Under the new runtime invariant this stops the runner at the first snapshot instead of exercising the intended quiet baseline, second-snapshot ordering or event draining. DEC-832 repairs **only these three tests** to obtain the actual newly generated sample's `os.lstat` device/inode while still mocking the snapshot bytes and retained synthetic event ordering. No runtime provenance check is bypassed.

Also ports the narrower unrelated fstat-mock repair from [#1043](https://github.com/Dtwosam/FMP/pull/1043): fake `fstat(19)` is scoped to that descriptor, while legitimate native tempfile cleanup's `fstat(3)` delegates to the original syscall. Original #1038 full CI recorded actual `[call(19),call(3)]` and remains RED.

**Test/docs-only**, strict immediate child of [#1042](https://github.com/Dtwosam/FMP/pull/1042), retaining **487 uniquely named source-defined methods**. Other legacy fake snapshot cases may still require exact-head CI diagnosis; do not claim full suite green. This is locally generated public Linux data, no OS confinement or run385 authority. Qualified review and exact-head Phase 3/full historical CI are necessary.

## DEC-833 — Preserve later negative controls after first-snapshot inode pin

DEC-830's stronger original O_EXCL writer / first watched snapshot equality check exposes inherited fixture inconsistency: two tests returned constant `(3,7)` instead of the actual native generated `sample` identity, and several hard-link/negative-control tests returned `(1,2)` despite using a genuine generated public inode. A false first baseline now stops before intended later snapshots, syscall failures or event draining. DEC-832 repaired three ordering tests, while this DEC-833 child repairs **twelve additional downstream-control test scopes**: the first fake snapshot obtains the actual newly generated file's device/inode via a shared native `os.lstat` helper, but leaves synthetic bytes, second-snapshot oversized/unexpected final fixtures, negative-control expected diagnostics and injected write, fsync and link errors intact. It never mocks or bypasses the new source-level inode continuity guard.

**Test/docs-only**, strictly child of [#1044](https://github.com/Dtwosam/FMP/pull/1044) with **487 source-defined distinct test methods** (none added). Other fake-alias scenarios remain for CI review; the current generated toy still cannot prove independently OS-enforced annual confinement, kernel provenance or run385 admission. Exact-head Phase 3/full historical CI and qualified security review required.

## DEC-834 — Restore precise hard-link second-snapshot contracts under inode pinning

The exact full historical run at [#1044](https://github.com/Dtwosam/FMP/pull/1044), [workflow 38138840119](https://github.com/Dtwosam/FMP/actions/runs/38138840119), failed 29 assertions (5,388 tests, 693 skips). The new original O_EXCL writer / first watched snapshot continuity guard rightly refuses an unrelated hard-coded mock inode `(1, 2)` before later hard-link alias and failure-control paths could execute. #1045 repaired 12 already identified fixtures; this child repairs **five further staged snapshot tests** whose first result must be the native generated sample inode but whose *second* result deliberately raises either a generic `OSError` or the specific `_SnapshotHardlinkCountError`. A tiny test-only helper preserves both the native first identity and the second stage's exact exception, keeping the intended finding assertions and alias helper recheck call counts active instead of allowing a false early block.

A sixth inherited test explicitly injects a wrong initial baseline inode `(0,0)`. Its previous expectation of reaching later alias-verification was made obsolete by the stronger guard: DEC-834 instead requires immediate `BLOCKED` before **any** `os.link` or `_plausible_generated_hardlink_pair` call, and verifies watcher FD cleanup. This is a more precise safety assertion, not a relaxation of the runtime guard.

**Test/docs-only** strict child of #1045; observer runtime unchanged, **487 uniquely named methods**. The failed #1044 ancestor CI remains RED and the #1045 full suite must retain its own independent verdict. New exact-head Phase 3/full historical CI and qualified independent source/security review remain necessary. This is only local generated Linux public witness work, not protected annual runner isolation or run385 authorization.

## DEC-835 — Integrate honest-return Path mutation guard and restore wrong-baseline content test

Separate sibling [#1048](https://github.com/Dtwosam/FMP/pull/1048), based on #1046, identified a previously untested synthetic watch-path wrapper: it mutates the actual concrete CPython `Path._raw_paths` during either `os.fspath` or `os.fsencode`, but returns the *unchanged old* valid target text or bytes. The earlier comparison could be deceived because the returned value remained correct. DEC-835 ports that runtime hardening and its targeted single-method regression to the [#1047](https://github.com/Dtwosam/FMP/pull/1047) descendant rather than merging or changing any sibling PR. The source retains a plain immutable tuple snapshot of originally validated segments and checks the actual raw segment list remains exactly identical after each potentially injected wrapper. If not, it fails closed before watcher registration. CPython-specific same-process input integrity is **not** a race-free kernel path-binding mechanism.

DEC-835 also repairs one *preexisting false-positive fixture*: `test_generated_runner_rejects_wrong_baseline_fixture_before_mutation` formerly supplied mismatched inode `(3,7)` along with wrong baseline bytes, so the stronger first-baseline identity guard now blocked before the intended **incorrect-content** contract. The test supplies the real generated native inode with unchanged `UNEXPECTED INITIAL` bytes, ensuring the check advances to the intended bytes mismatch, and still requires no event drain and watcher FD cleanup.

One new method raises the strict integrated suite from **487 to 488**. Changes are confined to disposable observer script, tests and docs. The #1048 sibling and #1047 ancestor CI records remain independent. Exact-head Phase 3/full historical CI and qualified source/security review remain required; not independent OS isolation or annual run385 admission.

## DEC-838 — Pin the generated parent directory across watcher setup and final inventory

Even with the DEC-827/830 original exclusive sample FD and watched baseline inode continuity checks, the disposable toy did not separately bind the **generated private parent-directory inode** after watch registration. A substituted `/tmp/dec677-disposable-*` pathname could otherwise cause inventory and child snapshots to refer to a different directory than the one initially validated, while old file/directory watch descriptors remained nominally identified.

DEC-838 captures the generated `0700` owner-private directory's bounded plain integer `(st_dev, st_ino)` via no-follow `lstat` before the initial public write, and repeats an equivalent validated identity check after dual watcher registration and immediately before final directory inventory. Any malformed metadata, lost private permissions/ownership, or changed device/inode emits `BLOCKED` before accepting a local witness. Two new source-defined regressions (now **490** on this strict line) check invalid directory metadata and instrument genuine Linux generated `/tmp` folders with a synthetic single-call inode substitution at each boundary, requiring early block, no event drain, and closed mock watcher FD.

The separate `os.lstat` calls are **not atomic with concurrent renames** or an independent kernel security boundary; no directory FD pin, openat2 resolution, mount-namespace isolation, or authenticated host no-write enforcement is claimed. The fixture does not mutate protected annual inputs or production configuration. Exact-head Phase 3 and full historical CI, and qualified independent security review, remain prerequisites. The immutable annual run385 admission and 20-job confinement gates remain BLOCKED.

## DEC-839 — Keep the earliest correct forged-path refusal under historical CI

Full historical [#1050](https://github.com/Dtwosam/FMP/pull/1050) workflow [38140381362](https://github.com/Dtwosam/FMP/actions/runs/38140381362) completed **RED**: 5,389 tests, two failing subtests, 693 skipped. Both failures were in the inherited mutating-fspath wrapper test: the stricter DEC-835 guard correctly detects changes to the source Path's stored segments and raises `raw segments changed during encoding` *before* the old comparison would raise `fspath disagrees`. The tested path remains rejected before byte encoding; only the expected first diagnostic was obsolete.

This test/docs-only immediate descendant of #1052 changes that one expected error phrase without weakening the observer source, early rejection, or no-encoder checks. The original #1050 full CI remains RED; the new exact head needs its own Phase 3 and full historical suite. **490 distinct test methods** remain.

## DEC-840 — Recheck the generated private directory after bounded final inventory

DEC-838 checked the generated `0700`, effective-user-owned `/tmp/dec677-disposable-*` directory's `(st_dev,st_ino)` just **before** final bounded inventory. That left a separate pathname-swap interval *while the final directory entries were read*. DEC-840 rechecks bounded plain directory metadata and matches the initial directory identity immediately **after** the second bounded scan, before event draining or returning a local witness. It refuses missing, malformed, no-longer-private and changed-inode parent directories even if the inventory still lists the ordinary `sample`.

Two native generated Linux `/tmp` tests inject a parent inode or privacy change at precisely the **post-inventory** probe, or an `OSError`/`RuntimeError` when probing at that same point. They require `BLOCKED`, no event draining, both immutable authorization booleans false and closed synthetic watcher FD. No protected annual inputs are touched. This raises the strict #1053 descendant from **490 to 492 distinct source-defined methods**.

These repeated pathname-level `lstat` checks cannot guarantee race-free parent binding or independent OS confinement; only real directory-FD-relative kernel resolution and authenticated host sandboxing could underpin stronger claims, neither implemented here. Exact-head Phase 3 + full historical CI and qualified independent review still required; run385 dispatch remains blocked.


## DEC-841 — Validate parent directory once more after event draining

DEC-840 checks the generated parent directory's private mode, owner, and
`(st_dev, st_ino)` after the final inventory but **before** draining the
inotify queue. A synthetic pathname substitution inside the drain could
otherwise reach the evaluator after the last parent identity validation.
DEC-841 validates the same original parent inode again after `_read_pending`
and before `_evaluate`, blocking on changed identity or failed metadata
probes. A new Linux-generated regression method injects either a different
directory inode or an `OSError` at this exact postdrain boundary. Both require
`BLOCKED`, no evaluator call, nonauthorization, and watcher FD cleanup.
The strict line now contains **493 uniquely named source-defined methods**.

Like the earlier path-based checks, this is a **non-atomic observation**, not
kernel-enforced path confinement. It does not guarantee absence of races after
the final probe, privileged writes, or protected annual-runner isolation.
This child requires separate exact-head Phase 3 and historical CI plus
qualified independent review. DEC-650/651 annual no-write confinement and
immutable run385 admission remain blocked. **DRAFT / NEVER MERGE**.


## DEC-842 — Recheck the watched disposable sample inode after event draining

The DEC-841 postdrain probe protects the **parent** identity, but a synthetic
same-directory replacement can leave that parent inode unchanged while
changing the basename `sample` after its last snapshot. DEC-842 adds a
bounded no-follow `lstat` check of the watched sample immediately before the
disposable evaluator, matching the original exclusive-writer FD's recorded
inode. An unexpected replacement, malformed sample identity or failed stat
blocks without evaluator entry. The intentionally generated
`replace_watched_inode=True` negative control is exempt from this early
refusal so its original replacement-detection evidence remains exercised and
non-authorizing. A new Linux fixture-driven regression covers a forged inode
and a stat failure arising during event drain. It requires `BLOCKED`, zero
evaluator calls, false authorization booleans and FD cleanup. **494 distinct
source-defined tests** now appear on the strict integrated line.

This is still **not atomic confinement**, does not detect a same-inode
write/revert after the final bytes snapshot without trustworthy events,
and cannot provide DEC-650 independent OS no-write proof or DEC-651 immutable
run385 admission. Exact-head Phase 3/full historical tests and independent
security review are still required. **DRAFT / NEVER MERGE**.


## DEC-843 — Detect late sample truncation or growth while draining events

DEC-842 rechecks the watched sample inode after event draining but, for a
same-inode late truncate or append, the existing inode check can still pass
although the previously captured final bytes are stale. DEC-843 checks the
original generated `sample`'s exact bounded plain integer `st_size` in
the same postdrain no-follow `lstat` record before entering the evaluator.
A length other than the fixed public `BEFORE` fixture, or malformed size
metadata, returns `BLOCKED`. The intentional inode-replacement negative
control retains its own evaluator path and never authorizes.

One Linux regression method changes **only** the generated public sample
bytes during the synthetic event drain, once by truncation and once by
appending, while preserving the original inode. Both cases require no
evaluator call, false authorization booleans and closed mock watcher FD.
**495 distinct source-defined tests** on the strict line.

Size alone cannot detect a same-length late overwrite, nor can sequential
pathname probes close kernel races. This is local witness hardening, not
an independent OS no-write proof or annual-runner authorization. DEC-650
and DEC-651 remain blocked; exact-head Phase 3 and full historical CI
plus qualified independent review are required. **DRAFT / NEVER MERGE**.

## Important limitations

**inotify is event observation, NOT OS write prevention.** It does not stop a privileged writer, make a read-only checkout, authenticate the observer process, protect against queue overflow or missed windows between installing/removing watches, cover arbitrary writable inode aliases, handle all mount namespaces or guarantee audit completeness after a malicious process tampers with the collector. It is especially not a substitute for independently enforcing a no-write sandbox. The demonstration uses its own unprivileged process to generate and collect events; the observer is not a separately trusted runner service.

No actual 20-job annual preflight+18 cell+freeze observer evidence, protected data, publisher receipt or authenticated kernel security profile is provided. DEC-650 draft #820 real OS confinement and DEC-651 draft #821 / issue #779 exclusive server-side immutable one-shot dispatch remain BLOCKED. Green synthetic tests do not authorize annual run 385.

**Hard stops:** no merge/ready promotion, actual 385 dispatch/test/rerun/retry, protected annual artifact reads, main/refs/workflow/ruleset/permission/runner changes, broker or trading action.
