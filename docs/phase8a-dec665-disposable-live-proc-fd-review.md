# DEC-665 — Disposable live-process procfs descriptor observer

**SOURCE-ONLY · DRAFT / NEVER MERGE · never annual authorization.**

This is a narrow, offline Linux observer prototype for the *while-running* descriptor portion of the actual OS-isolation acceptance contract in DEC-650 draft #820. It does not run on or authorize the annual GitHub runner, and it cannot dispatch annual run 385.

## What the separate parent observes

The demo creates a brand-new temporary synthetic checkout and scratch directory under fixed /tmp, writes a public placeholder file, and opens that file in the parent before child launch. The child is a fixed Python one-liner launched with explicitly controlled PATH/LANG, stdout/stderr pipes, stdin pipe, close_fds=True, and working directory set to separate scratch. It emits a one-byte readiness marker, flushes stdout and pauses waiting for a byte from the parent.

**While the child is still alive at its readiness barrier**, the parent reads that child's /proc/PID/fd directory symlink targets and /proc/PID/cwd path. The parent checks that FD0/FD1/FD2 targets are all pipes, no unexpected FDs are visible, no target references the fake checkout, and the child's cwd is the synthetic scratch directory. After the snapshot, it releases the child and requires a clean exit with no other stdout/stderr output.

Two mutually exclusive explicit modes:

    python -B scripts/dec665_live_proc_fd_observer.py --execute-disposable-demo
    python -B scripts/dec665_live_proc_fd_observer.py --execute-fd-negative-control

In the negative control, the parent deliberately passes an already-open writable descriptor for the **public disposable fake checkout file** using pass_fds. The live parent scan sees the file target and extra FD; the outcome is BLOCKED, exit 2. In the clean mode, the parent preopens the same FD but does not pass it, observes only the three approved pipe descriptors and separate cwd; the result is LOCAL_DISPOSABLE_WITNESS_UNVERIFIED, exit 3.

If /proc inspection is unavailable or ambiguous, readiness times out, the child exits abnormally or any observed check fails, the result is BLOCKED. The CLI without opt-in is inert BLOCKED exit 2. No caller-selected file or credential path is accepted and no raw proc target paths, secret strings or host metadata are printed. Every result has can_authorize_dispatch=false and independent_os_proof_verified=false.

The 16 source-defined tests include two *explicitly opt-in* live Linux observations, skipped in regular CI; the other cases use synthetic field failures, malformed claims, rejected options and nonauthorization assertions.

## DEC-666 pinned double-snapshot stability check

The original DEC-665 parent scanned a live child's /proc/PID/fd symlink table only **once**. A process that closed/replaced a descriptor or changed its working directory during the read could have produced a mixed-time observation. This revision opens and holds an **O_NOFOLLOW directory FD** to the child's procfd directory, enumerates targets relative to that pinned directory (readlinkat-style, without opening the target files), and takes **two independent immediate scans**. It also reads /proc/PID/cwd twice. Any difference in either FD table or cwd fails closed, rather than silently treating the observation as internally consistent.

Four additional synthetic tests (total **20 source-defined tests**, including two opt-in Linux demonstrations) cover consistent snapshots, new/changed FD targets, changed cwd and FD-relative symlink reading. The observer still returns no actual paths or token values to the caller, and all results remain nonauthorizing.

**Important limitation:** two consistent snapshots do NOT establish that a malicious child cannot close and reopen dangerous handles before, between or after them. A stronger child can fork, change namespace or escape the toy readiness barrier, and a host principal can interfere with /proc. This remains offline process-observer research, not DEC-650 actual runner independent security attestation.

## Security scope and critical limitations

Unlike a child that self-reports its own file descriptors after termination, this experiment has a distinct parent **inspect a running child** before releasing it, but this alone does not create a trusted attestation or close all TOCTOU windows. The child is not a real annual CLI and does **not** enforce a non-owner UID, mount namespaces, capability/seccomp policy or deny all host-side aliases. The parent is only trustworthy under a hypothetical trusted host setup; /proc may be denied or manipulated by a stronger host principal. A one-time snapshot cannot ensure that a process never acquires new FDs after release. A malicious child could also fork, reassign descriptors or escape the simplistic one-byte barrier; this hardcoded child deliberately does not exercise those cases.

The **actual** DEC-650 matrix requires independent proof for preflight + 18 cells + freeze, real runner/container image and kernel identity, all aliases and sibling writers, descriptors, token/environment/argv sources, a trusted report uploader, no skips and reviewed failure behavior. This toy observer meets **none** of those privileged acceptance conditions on the actual annual runner.

The independent DEC-651 draft #821 / issue #779 mutable-main ref and server-exclusive one-shot workflow dispatch gate is also BLOCKED. No synthetic result changes that.

No protected annual artifact reads, code/trades, ref/workflow/tag/ruleset/permission/runner mutation, merge, ready-for-review promotion, or annual run385 dispatch, test dispatch, retry or rerun is authorized or performed.
