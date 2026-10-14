# DEC-1086 — Watched-directory self-read event identity and one-shot lifetime matrix

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of DEC-1085/#1306 at 604217ac399d970a41353fef51cfb0a3d55c25a0. **710 source-defined test methods unchanged**; exactly one new Markdown review. No runtime, executable, production, protected annual, broker or trading change.

## Three benign read operations affecting the *watched directory inode itself*

| Regression | Subscription that is intentionally first-match one-shot | Genuine initial PUBLIC operation | Original one-shot event(s) | Separate continuing parent witness | Subsequent unsafe activity seen only independently |
| --- | --- | --- | --- | --- | --- |
| DEC-1082/#1303 | IN_OPEN plus CREATE/DELETE/MODIFY/CLOSE_WRITE; IN_ONESHOT | Read-only O_DIRECTORY open of **watched parent inode** | **Unnamed IN_OPEN|IN_ISDIR**, then IN_IGNORED | Unnamed IN_OPEN|IN_ISDIR | Real sample MODIFY/CLOSE_WRITE source + named parent |
| DEC-1084/#1305 | IN_CLOSE_NOWRITE plus CREATE/DELETE/MODIFY/CLOSE_WRITE; IN_ONESHOT; **OPEN and ACCESS excluded** | Read-only open of watched directory (initially quiet), then **close** | **Unnamed IN_CLOSE_NOWRITE|IN_ISDIR**, then IN_IGNORED | Unnamed IN_CLOSE_NOWRITE|IN_ISDIR | Real sample MODIFY/CLOSE_WRITE source + named parent |
| DEC-1085/#1306 | IN_ACCESS plus CREATE/DELETE/MODIFY/CLOSE_WRITE; IN_ONESHOT; **OPEN and CLOSE_NOWRITE excluded** | Actual **os.scandir enumeration** of watched directory entries | **Unnamed IN_ACCESS|IN_ISDIR**, then IN_IGNORED | Unnamed IN_ACCESS|IN_ISDIR | Real sample MODIFY/CLOSE_WRITE source + named parent |

All three use freshly generated PUBLIC disposable Linux /tmp fixtures. The original unsafe test-only parent IN_ONESHOT watch and benign-event witness are created by separate native inotify_init1 calls; a further independently initialized full source+parent mutation watcher observes actual later source bytes changing and writable closes, including a final real restoration write. These are observations of real successful local filesystem operations, not synthesized receipts. The later original one-shot queue is empty because the kernel already delivered IN_IGNORED and removed the registration. Subscription to MODIFY and CLOSE_WRITE does not supply events after watch destruction.

An unnamed event with IN_ISDIR describes the directory inode itself. It is **not** a named child mutation and must not be conflated with earlier sibling OPEN/ACCESS/CLOSE_NOWRITE regressions (#1292/#1297/#1298), which carry the sibling's filename. Similarly, IN_ISDIR modifies a single primary OPEN, ACCESS or CLOSE_NOWRITE event; it does not constitute an independent CREATE/DELETE or extra event record. Successful benign directory opening, enumeration or closing is not a protected-write action, but it can consume an intentionally unsafe one-shot watch's entire later event coverage.

## Boundary of the evidence

A final equal PUBLIC sample digest, unchanged source+parent dev/inode/mode and bounded final directory-name inventory cannot recover native event history missed after IN_IGNORED. It also cannot independently OS-enforce protected annual no-write. The actual unchanged observer scripts/dec677_disposable_inotify_events.py::_start_watch uses continuing source+parent **mutation** watches, without IN_ONESHOT or the benign read-category subscriptions in these alternative regressions. Do not characterize these controls as evidence of an installed observer runtime vulnerability.

The evaluator remains exact status=BLOCKED, can_authorize_dispatch=false, independent_os_proof_verified=false when genuine independent unsafe native mutation receipts are supplied. A local quiet disposable witness returns distinct LOCAL_DISPOSABLE_WITNESS_UNVERIFIED, never an annual dispatch authorization.

## CI provenance and immutable admission

At this review's preparation, #1300/DEC-1079 was the latest consecutively verified exact-head Phase 3 + full historical CI checkpoint with **706 source-defined tests**; #1302 individually had passed both suites while #1301 remained pending. Each descendant #1301–#1307 requires **both** suites finished successfully at its own exact commit before it is called fully CI verified, followed by separate qualified independent security review. Original failed exact historical commits #1201–#1205, #1212, #1237 and #1261–#1267 remain FAILED regardless of passing descendants.

Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. All children stay DRAFT / NEVER MERGE / NEVER PROMOTE. No protected annual source/evidence, run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading, merges or promotions.
