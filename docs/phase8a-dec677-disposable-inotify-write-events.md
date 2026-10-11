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

## Important limitations

**inotify is event observation, NOT OS write prevention.** It does not stop a privileged writer, make a read-only checkout, authenticate the observer process, protect against queue overflow or missed windows between installing/removing watches, cover arbitrary writable inode aliases, handle all mount namespaces or guarantee audit completeness after a malicious process tampers with the collector. It is especially not a substitute for independently enforcing a no-write sandbox. The demonstration uses its own unprivileged process to generate and collect events; the observer is not a separately trusted runner service.

No actual 20-job annual preflight+18 cell+freeze observer evidence, protected data, publisher receipt or authenticated kernel security profile is provided. DEC-650 draft #820 real OS confinement and DEC-651 draft #821 / issue #779 exclusive server-side immutable one-shot dispatch remain BLOCKED. Green synthetic tests do not authorize annual run 385.

**Hard stops:** no merge/ready promotion, actual 385 dispatch/test/rerun/retry, protected annual artifact reads, main/refs/workflow/ruleset/permission/runner changes, broker or trading action.
