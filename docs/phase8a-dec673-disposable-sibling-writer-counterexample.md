# DEC-673 — Disposable privileged sibling-writer counterexample

**DRAFT / NEVER MERGE. Source-only, local synthetic files, never annual authorization.**

A real Linux permission denial for a restricted consumer does not mean the underlying checkout file cannot be modified by another host principal with greater write authority. This is a specific unresolved threat-model gate from DEC-650 #820. It is not a new permission request and does not make the installed annual runner safe.

This opt-in Linux test creates a fresh fake checkout file under fixed /tmp, owned by an already-root local disposable parent. A hardcoded child launched with setpriv UID/GID65534, cleared groups/capabilities and no_new_privs pauses at a private pipe. Two independent modes are tested:

- **Control mode:** The restricted child attempts to truncate the fake checkout and receives kernel PermissionError. The root-owned fake file stays unchanged. Result LOCAL_DISPOSABLE_WITNESS_UNVERIFIED, exit 3. This remains nonauthorizing.
- **Privileged sibling negative mode:** While the restricted child is paused, the root parent intentionally overwrites the same public synthetic checkout file. The child still receives PermissionError for its own write. The parent independently detects changed SHA-256 bytes after the child exits and returns BLOCKED, exit 2. This demonstrates that *child UID restriction* and *host-wide source immutability* are different propositions.

Only generated public fixture bytes are used. No actual annual checkout, workflow, protected data, credentials, network endpoint or broker account is read or touched. The command requires pre-existing root and Linux setpriv; it does not run sudo or elevate other users. Without explicit opt-in it is inert and BLOCKED.

    python -B scripts/dec673_disposable_sibling_writer.py --execute-disposable-control
    python -B scripts/dec673_disposable_sibling_writer.py --execute-privileged-sibling-negative

The suite has **12 source-defined tests**, one manual opt-in Linux test skipped in standard CI. On a disposable local Linux root host both OS modes were reproduced and all 12 tests passed with opt-in. The negative mode returned BLOCKED while its restricted child still reported kernel denial.

**Limitations:** This is a scheduled synthetic change by a known privileged parent, not proof of an actual malicious sibling, writable bind alias, cross-mount reparenting or continuous race defense. Post-hoc checksum catches changed bytes here but does not prevent writes and cannot detect changes that are later reverted. Real DEC-650 isolation requires removal/restriction of all source-capable writer principals, checked continuously by a trusted independent observer. All 20 actual jobs and external uploader remain unverified. DEC-651 #821 / issue #779 one-shot immutable server dispatch is separately BLOCKED.

Every outcome has can_authorize_dispatch=false and independent_os_proof_verified=false. No merge, protected annual artifact access, actual annual run 385 dispatch/test/retry/rerun, main/refs/workflow/ruleset/permission/runner modification, broker or trading operation.
