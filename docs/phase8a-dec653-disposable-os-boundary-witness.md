# DEC-653 — Disposable Linux OS-denial witness

**DRAFT / NEVER MERGE. Source-only research. No annual workflow authorization.**

This independent test fixture explores a kernel-enforced read-only mount on a newly created, synthetic checkout. It is a small executable step toward reviewing the actual OS isolation contract in DEC-650 (draft PR #820); it is not a deployed annual runner sandbox.

## What the opt-in program does

1. Generates a disposable temporary checkout with one synthetic sample file and a separate external directory. It never accepts a source path supplied by the caller.
2. Within a fresh Linux user and mount namespace, makes the mount tree private, bind-mounts the synthetic checkout onto itself and marks that bind read-only.
3. Starts a new child with all capability sets required to be zero and no_new_privs enabled, redirecting standard input/output/error to non-source endpoints.
4. Attempts file creation, truncation, chmod, directory reparent/rename and remount. It checks a read-only mount observation, and the separate outer process compares its synthetic checkout contents and inventory after the experiment.
5. Always returns a nonauthorizing result. Missing commands, unsupported namespaces, failed setup, missing/failed denial checks, nonzero capability sets and inventory mutation become BLOCKED (exit 2). Consistent local synthetic observations become LOCAL_DISPOSABLE_WITNESS_UNVERIFIED (exit 3).

All output includes can_authorize_dispatch=false and independent_os_proof_verified=false. No result has a zero success exit code.

## Explicit use

Default safe command only prints BLOCKED and runs no namespace probe:

    python -B scripts/dec653_disposable_mount_witness.py

Optional disposable Linux experiment (only on a permitted local disposable host):

    python -B scripts/dec653_disposable_mount_witness.py --execute-disposable-demo

Synthetic unit regressions (real OS test skipped without explicit opt-in):

    python -B -m unittest discover -s tests -p 'test_dec653_disposable_mount_witness.py' -v

A reviewer may run the opt-in OS test with DEC653_EXECUTE_DISPOSABLE_OS_TEST=1, using their own disposable environment. The script requires the Linux unshare, mount and setpriv utilities and support for unprivileged user namespaces; unsupported hosts remain BLOCKED.

## DEC-654 deliberately injected preopened-FD counterexample

A second, mutually exclusive **opt-in mode** intentionally opens a writable descriptor to the temporary synthetic checkout **before** mounting the same directory read-only, then passes that descriptor to the otherwise restricted child. The child attempts a write through that preopened file descriptor. The outer parent detects changed source bytes and marks the result **BLOCKED** (exit 2), including a specific inherited-checkout-descriptor finding. In the local disposable Linux reproduction, the injected write succeeded despite all capabilities being zero and the bind mount showing read-only. This is a real local **negative counterexample** to treating read-only mounts as complete write isolation, not permission to access actual annual source.

    python -B scripts/dec653_disposable_mount_witness.py --execute-fd-counterexample

A normal, non-injected local demo reports the descriptor probe as not provided; any missing or injected descriptor provenance now forces BLOCKED. The 15 source-defined synthetic regression tests include explicit negative checks and two OS demonstrations **skipped by default**. The experiment is limited to internally generated temporary files and never accepts a repository source path.

**Required future OS boundary:** ensure trusted staging closes writable checkout descriptors (including descriptors 0/1/2 and parent/proc-fd aliases) *before* the restricted consumer starts, and independently prove no actor can reintroduce them. A mount-table snapshot by itself is insufficient. The demonstration itself does not implement that trusted end-to-end production lifecycle.

## Security limitations

This is a negative witness on a brand-new fake checkout, not an independently authenticated production report. The child supplies some of its own observations; a separate trusted observer has not verified its live mount table, UIDs, capabilities, descriptors, seccomp or environment across 20 real annual jobs. The experiment does not secure trusted staging, checkout aliases or sibling writers, the external uploader or race scheduling on the actual GitHub runner.

The experiment also cannot make the mutable main branch immutable or implement exclusive one-shot workflow admission (DEC-651 draft PR #821 and issue #779). Green CI and local synthetic denial results are never permission to consume annual run 385.

No real annual workflow, protected dataset, repository setting, branch/tag/ruleset, runner installation, broker or trading operation is changed by this branch. Independent code and OS security review remain prerequisites. Keep this PR in DRAFT / NEVER MERGE state.
