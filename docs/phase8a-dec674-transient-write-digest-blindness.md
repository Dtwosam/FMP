# DEC-674 — Transient write/revert bypasses before/after digest evidence

**DRAFT / NEVER MERGE. Source-only fake file; NO authorization.**

DEC-650 requires prevention of writes throughout each restricted job's lifetime. Comparing an inventory digest before and after a process is useful for detecting some mutations, but it does NOT prove no writes happened in between.

The explicit disposable negative control creates a new public fake file under /tmp. It records its original bytes and SHA-256, performs a first real write replacing them with a public alternate string, then performs a second real write restoring precisely the original bytes. Each write is flushed and fsynced. Final bytes and SHA-256 are **exactly unchanged**, despite two completed writes. A synthetic in-process write-event count records the two controlled operations and makes the verdict BLOCKED, exit 2. This is a deterministic demonstration of a digest-only proof's blind spot, not an OS-enforced write monitor or trusted kernel audit.

The clean disposable control performs no writes and yields only LOCAL_DISPOSABLE_WITNESS_UNVERIFIED exit 3. A missing, invalid or untrusted event count always blocks even when hashes match. Output never contains any host paths or real data and always sets can_authorize_dispatch=false, independent_os_proof_verified=false.

Commands (no caller-provided paths accepted):

    python -B scripts/dec674_disposable_transient_write.py --execute-disposable-control
    python -B scripts/dec674_disposable_transient_write.py --execute-reverted-write-negative

**12 source-defined synthetic tests** have passed locally, including the actual temporary write/revert scenario. The event counter is a test-only hook under the writer's control; it is not independently attested and cannot prove a genuine zero-write run. An actual annual runner would need enforceable prevention, trusted continuous observations or independently justified equivalent policy, not a self-reported event count or post-hoc checksum.

Separate DEC-650 #820 OS enforcement, writer principal containment, 20 actual annual jobs, trusted uploader and independent observer remain BLOCKED. DEC-651 #821 / issue #779 exclusive immutable one-shot dispatch admission remains BLOCKED. No merge, run 385 test/dispatch/retry, protected annual data, main/workflow/ref/ruleset/permissions/runner mutation or trading activity.
