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

## DEC-655 checked closure of a preopened writable descriptor

The predecessor DEC-654 compares a clean mode that did **not open** the writable checkout FD with an injected mode that did. This revision strengthens the comparison: **both** modes open the same disposable writable checkout file before the readonly remount, duplicating it to high FD 200+ with CLOEXEC. In the clean mode the parent starts the child with close_fds=true and **does not** opt that FD into pass_fds. The restricted child attempts os.write against the advertised high FD and observes EBADF, recorded as closed_before_consumer. The resulting local verdict is only LOCAL_DISPOSABLE_WITNESS_UNVERIFIED (exit 3).

In the adversarial opt-in mode, the parent explicitly adds that high FD to pass_fds. The restricted child can write through the already-open handle despite the readonly bind mount; the parent sees changed *synthetic* inventory and returns BLOCKED (exit 2). Both outcomes keep can_authorize_dispatch=false and independent_os_proof_verified=false. This is a **limited local comparison**, not a general audit of all inherited descriptor targets or production runner isolation.

The synthetic temp checkout is now rooted at fixed /tmp instead of honoring caller-provided TMPDIR, and the parent snapshots the fake source by a pinned directory descriptor and O_NOFOLLOW regular-file opener. It caps snapshot bytes at 4 KiB, compares inode identity and contents, and avoids following a swapped sample symlink when checking the child result. A host where /tmp is a symlink or missing is BLOCKED. These changes are local-test input protections, not hardening installed annual sources or proof against malicious sibling writers.

There are **23 source-defined regression tests**; 2 optional Linux OS demonstrations are skipped in ordinary CI. The separately executed opt-in disposable Linux suite passed 23/23 on the local test host. Independent source review and current exact-head GitHub CI remain necessary.

## DEC-656 FIFO and directory-swap input safety

A further local read-path review found that O_NOFOLLOW by itself does **not** prevent blocking on a FIFO substituted for a previously regular file. A concurrent writer could cause the bounded parent snapshot to stall before its fstat check. The local synthetic snapshot now opens with **O_NONBLOCK** in addition to O_NOFOLLOW; non-regular FIFOs are rejected by fstat without waiting for a writer. A subprocess regression exercises a synthetic FIFO and requires termination within three seconds.

The second new regression replaces the disposable checkout directory pathname with a symlink while the parent retains the original directory descriptor. The final comparison must reject the changed directory inode rather than following the replacement. This remains a disposable, synthetic demonstration of failure handling; it does not address real annual-runner sibling-write authority.

**25 source-defined tests** are now present; the same two actual Linux mount demonstrations require manual opt-in and are skipped in default CI. These tests passed both default and opt-in local runs; current-head GitHub CI and an independent reviewer still remain mandatory.

## DEC-657 standard-output file-descriptor counterexample

DEC-655 proved that close_fds=true closes high-numbered preopened file handles. **It does not establish safety of standard descriptors 0/1/2.** The new manual \`--execute-stdio-counterexample\` mode deliberately installs the already-open writable synthetic checkout FD as restricted-child **standard output (FD 1)**, without opting a high-numbered FD into pass_fds. The restricted child writes a short marker to stdout through that preopened handle; the readonly bind mount still denies ordinary path writes but the synthetic sample bytes change. The parent independently detects changed inventory and returns **BLOCKED**, exit 2, with a standard-stream finding. Structured untrusted child diagnostic data is emitted through a separate captured stderr pipe in this intentionally adversarial mode.

Normal opt-in and high-numbered-FD counterexample modes continue to use explicitly captured pipes for stdout/stderr and \`/dev/null\` for stdin. The three run modes are mutually exclusive at the CLI. All modes remain restricted to newly created disposable files, nonauthorizing, with no actual FMP annual checkout, protected-data, workflow or trading access.

Local default regression result: **30 defined tests, 3 manual Linux demonstrations skipped**. With explicit local opt-in, **30/30 passed**, including the new standard-output writable-handle negative witness. None of these results can be promoted into actual runner acceptance without independent OS measurements and a reviewed trusted staging/uploader boundary; this is only a local negative control.

Manual example on a permitted disposable Linux host:

    python -B scripts/dec653_disposable_mount_witness.py --execute-stdio-counterexample

## DEC-658 standard-input FD0 synthetic canary disclosure

The previous experiments demonstrate dangerous *write* authority inherited through high file descriptors and stdout (FD1). This revision demonstrates a separate **read/confidentiality** boundary: an untrusted child may inherit a privileged input handle as **stdin (FD0)**, even when the checkout is mounted read-only, process capabilities are zero, and the child environment is reduced.

The new opt-in \`--execute-stdin-counterexample\` mode creates a short **public, hard-coded fake credential** inside its disposable external directory, opens it read-only, and gives that opened descriptor to the restricted child's stdin. The child reads FD0, compares bytes against the public fixture (without printing or storing sensitive data) and records \`stdin_probe=canary_received\`. The parent treats every value other than \`safe_eof\`, including an absent claim, as **BLOCKED** (exit 2). The fake source checkout remains unchanged in this read-only disclosure case. A normal disposable child uses stdin=/dev/null, observes EOF and receives only \`LOCAL_DISPOSABLE_WITNESS_UNVERIFIED\` (exit 3); this status never grants approval.

All four explicit modes are mutually exclusive. Only a fixed public synthetic string and internally generated temporary files are involved; no repository, real tokens, environment secrets, runner credentials, protected evidence, or broker connection is accessed. This child self-report is **untrusted** and cannot substitute for independent observer inspection of real FD0/1/2 symlink targets, permissions, or readable aliases.

**36 source-defined regression tests** now cover the FD0 canary and negative claims, including four optional Linux OS demos (skipped in standard CI). Local regression and manual-mode validation are author-side only; independent exact-source CI/security review remain mandatory. DEC-650 real OS isolation and DEC-651 one-shot dispatch admission remain BLOCKED.

Manual disposable mode:

    python -B scripts/dec653_disposable_mount_witness.py --execute-stdin-counterexample

## DEC-659 synthetic environment credential-inheritance counterexample

A read-only mount, emptied inherited file descriptors, safe FD0/FD1/FD2 bindings and cleared Linux capabilities do **not** by themselves guarantee that the restricted child receives no confidential environment values. The opt-in \`--execute-env-counterexample\` mode demonstrates this distinct process-boundary failure by adding a fixed **public synthetic canary**, \`DEC659_SYNTHETIC_ACCESS_TOKEN=DEC659_PUBLIC_FAKE_CANARY\`, to that disposable child's explicitly controlled environment.

The restricted child reports **only** \`env_probe=canary_present\`; the canary value is never emitted into stdout or stored in a report. The parent treats every value except \`env_probe=absent\` as **BLOCKED** (exit 2), even if the fake checkout inventory has not changed. In the normal mode, the child's environment has only specified PATH and LANG, the canary is absent and the local result remains \`LOCAL_DISPOSABLE_WITNESS_UNVERIFIED\` (exit 3) — never a security PASS.

Five manual Linux modes are now mutually exclusive: normal, inherited high writable FD, writable stdout FD1, readable stdin FD0 synthetic canary, and environment synthetic canary. All public fixtures are created inside an internal temporary sandbox. No real token, password, broker credential, protected annual artifact, or network service is accessed.

The suite now has **42 source-defined tests**, including five manual OS demonstrations that ordinary GitHub CI skips. Author-side local results are not independent OS proof. A qualified real runner review must verify actual environment names and handling, values without disclosing them, argv/proc and FD inheritance, independent credentials audit, uploader boundary and all 20 annual jobs.

## DEC-660 synthetic command-line (argv) canary exposure

An attacker-readable process argument is a **third independent leak path** beyond file descriptors and environment variables. Even if the restricted consumer has no inherited writable checkout handles and the environment is cleaned, embedding a secret in its command line can expose it to process introspection, diagnostics or logs.

The new opt-in \`--execute-argv-counterexample\` mode appends an entirely **public synthetic marker**, \`DEC660_PUBLIC_FAKE_ARGV_CANARY\`, to the restricted child's command arguments. The child reports **only a category** \`argv_probe=canary_present\`; the parent returns **BLOCKED** (exit 2). A missing/unexpected argv claim also blocks. The normal mode passes no extra argument, observes \`argv_probe=absent\`, and still returns only \`LOCAL_DISPOSABLE_WITNESS_UNVERIFIED\` (exit 3). Every result continues to set \`can_authorize_dispatch=false\` and \`independent_os_proof_verified=false\`.

The six explicit mutually exclusive disposable modes now test normal closed handles and five negative controls: high-FD write, FD1 stdout write, FD0 public canary read, public environment variable canary, and public argv canary. The code never handles real tokens, protected annual data, broker parameters or another checkout. It does not contact the network or run the annual workflow.

There are **48 source-defined tests**, including six manual opt-in Linux demonstrations skipped during normal CI. Author-side local test replication verified 41 cases with 3 older demonstration skips while directly executing the new argv observation. **No independent real-runner proof or CI acceptance is implied.**

## Security limitations

This is a negative witness on a brand-new fake checkout, not an independently authenticated production report. The child supplies some of its own observations; a separate trusted observer has not verified its live mount table, UIDs, capabilities, descriptors, seccomp or environment across 20 real annual jobs. The experiment does not secure trusted staging, checkout aliases or sibling writers, the external uploader or race scheduling on the actual GitHub runner.

The experiment also cannot make the mutable main branch immutable or implement exclusive one-shot workflow admission (DEC-651 draft PR #821 and issue #779). Green CI and local synthetic denial results are never permission to consume annual run 385.

No real annual workflow, protected dataset, repository setting, branch/tag/ruleset, runner installation, broker or trading operation is changed by this branch. Independent code and OS security review remain prerequisites. Keep this PR in DRAFT / NEVER MERGE state.
