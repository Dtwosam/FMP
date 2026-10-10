# DEC-672 — Parent-observed live separate-UID disposable witness

**DRAFT / NEVER MERGE. NONAUTHORIZING. Source-only, fake files only.**

This source-only research follows DEC-669 draft #840. Its purpose is to reduce reliance on a restricted child's claims by having a different parent process inspect the child's kernel-reported state **while it is paused and alive**, before allowing synthetic denied writes. It does not invoke the installed annual workflow, fetch protected evidence or interact with GitHub dispatch, permissions or trading.

## Method

An already-root Linux test process (with explicit opt-in) creates public synthetic source, root-owned external report and scratch directories under fixed /tmp, and starts a hardcoded child via setpriv UID/GID 65534, cleared groups/capabilities and no_new_privs. The child emits one readiness byte, then pauses at a private stdin pipe. Its parent examines /proc/PID/status for four real/effective/saved/filesystem UID and GID fields, supplementary groups, all four CapEff/CapPrm/CapBnd/CapAmb capability sets, and NoNewPrivs. It also tries *two immediate snapshots* of /proc/PID/fd symlink targets and /proc/PID/cwd. All stdio targets must be pipes, no extra FDs or checkout/report handles may be observed, cwd must be the fake scratch directory, and the two snapshots must be internally consistent. Finally the parent releases the child to attempt denied source/report writes and independently checks both fake file inventories unchanged.

There is a negative control: the parent deliberately passes a writable fake checkout FD in pass_fds. It MUST produce BLOCKED even if the child does not write through it. All raw /proc targets, credentials and fixture paths are suppressed in output. No caller-provided checkout, repo or source paths are accepted.

### Tested local /proc privilege blocker

An actual root UID in the available disposable Linux container **cannot dereference the other-UID child's /proc/PID/fd symlink targets or /proc/PID/cwd**: Linux returns PermissionError under its ptrace-access restrictions. The parent's /proc/PID/status is still readable and correctly observes UID/GID 65534, zero capabilities, and NoNewPrivs=1. This prototype explicitly marks the unreadable FD/cwd observations false, and the outcome **BLOCKED exit 2**, not a synthetic pass. It never suggests granting ptrace rights on a production runner. Any host privilege change would need a separately reviewed threat model.

The local synthetic suite has **14 defined tests**, 1 local OS opt-in demonstration skipped by default. Default local run: 14 tests OK (1 skipped). Explicit local OS run: 14 tests OK (0 skipped); both normal and injected demonstrations remain BLOCKED on the current host due to /proc FD/cwd access restrictions. All outcomes maintain can_authorize_dispatch=false and independent_os_proof_verified=false, including on a host where a clean toy observation might produce LOCAL_DISPOSABLE_WITNESS_UNVERIFIED exit 3.

Run default inert CLI:

    python -B scripts/dec672_disposable_live_uid_observer.py

Run opt-in only on an authorized disposable Linux sandbox:

    python -B scripts/dec672_disposable_live_uid_observer.py --execute-disposable-demo
    python -B scripts/dec672_disposable_live_uid_observer.py --execute-leaked-fd-control

One parent snapshot—even doubled—cannot establish continuous containment of a hostile child, prevent root/sibling alias writes, substitute for a trusted observer, or prove correct staging/publisher authority. This fixed toy child is not any of the 20 annual workflow jobs. Real DEC-650 #820 all-20-job OS evidence, external uploader receipts, independent human review and DEC-651 #821/issue #779 server-exclusive immutable one-shot admission remain separate **BLOCKED** gates.

**Hard stops:** no merge, protected annual data, real run385 dispatch/test/retry/rerun, main/workflow/branch/tag/ruleset/permission/runner mutation, broker or trading action.
