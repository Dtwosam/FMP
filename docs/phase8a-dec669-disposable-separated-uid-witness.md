# DEC-669 — Disposable separate-UID checkout and publisher boundary

**DRAFT / NEVER MERGE. RESEARCH-ONLY. NO annual run 385 authority.**

This is a distinct local OS permissions witness supporting the future DEC-650 #820 annual runner isolation review. It is **not installed** in the annual workflow. No protected annual source, broker, GitHub credential, trading data or control-plane resource is used.

Unlike child self-reported read-only mount status or only a post-hoc hash, the test actually launches a synthetic consumer using Linux setpriv with **UID/GID 65534**, cleared supplementary groups, cleared bounding/inheritable/ambient Linux capabilities, and no_new_privs. The trusted setup runs only when the caller is ALREADY UID 0 and explicitly opts in; it does not call sudo or elevate anyone. On hosts lacking root, setpriv or Linux /proc, the result is BLOCKED.

The trusted parent creates a temporary tree under fixed /tmp: a public readable source with a root-owned fake file and no directory write permission for the consumer; a separate root-owned external report directory mode 0700 with a report mode 0400; and a disposable writable scratch directory. The child receives an explicit minimal environment and safe subprocess standard streams. Its attempted path writes (create, truncate, chmod, directory reparent) into source and reads/writes into the external publisher directory must receive kernel PermissionError, while the public source remains readable and scratch is its cwd. Parent separately verifies source bytes, report bytes, names and SHA-256 are unchanged.

Use default inert path:

    python -B scripts/dec669_disposable_uid_boundary.py

Explicit **local disposable root-only** experiment:

    python -B scripts/dec669_disposable_uid_boundary.py --execute-disposable-demo

Synthetic regression suite (one actual OS test skipped by default):

    python -B -m unittest discover -s tests -p 'test_dec669_disposable_uid_boundary.py' -v

To opt in to the real local OS test only on an authorized disposable Linux host, set DEC669_EXECUTE_DISPOSABLE_UID_TEST=1. A local disposable container run produced 15 true observations and a LOCAL_DISPOSABLE_WITNESS_UNVERIFIED status (exit 3); all 9 local tests passed when opt-in was enabled, and all 9 passed with 1 skip by default.

**No approval can ever result.** Default/unsatisfied prerequisites = BLOCKED exit 2; all synthetic denials observed = LOCAL_DISPOSABLE_WITNESS_UNVERIFIED exit 3. Every outcome contains can_authorize_dispatch=false and independent_os_proof_verified=false.

**Limitations:** This uses a simple root-owned temporary directory and permission-bound child, NOT a real annual runner, reviewer-attested mount topology, hardened namespaced container, lifetime FD audit or independent policy enforcement for preflight + 18 matrix jobs + freeze. The child report includes self-observed credentials (the host did not independently snapshot all properties); writable aliases, malicious root/sibling processes, network/syscall policy, trusted setup dependencies and external GitHub artifact receipt are not proven. Do not mistake UID 65534 or 0700 alone for end-to-end annual isolation. Real DEC-650 #820 and DEC-651 #821/issue #779 immutable exclusive one-shot dispatch remain BLOCKED.

Hard stops: no merge/promotion, no annual run385 dispatch/test/rerun/retry, no protected artifact access, no main/workflow/runner/tag/ruleset/permissions mutation or trading/broker action. Independent code and actual-runner OS security reviews remain mandatory.
