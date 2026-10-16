# DEC-1320 — Independent protected no-write and exclusive annual admission: fail-closed acceptance contract

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of #1543 DEC-1319 at `33b0725bbfb415ec8ef7c8cf53d8fdbdce92da36`. **878 distinct source-defined tests unchanged**. No protected annual source/evidence access, no installed workflow or runner change, no production/trading/broker operation, no protected dispatch, and no authority upgrade.

## Why a separate acceptance contract is required

The existing [DEC-624] three-layer admission ordering model (`docs/phase8a-2023-run385-three-layer-ref-sha-admission-model.md`) is explicitly **SOURCE-ONLY / UNINSTALLED / NONAUTHORIZING**. The existing run-385 administrator handoff (`docs/phase8a-2023-run385-admin-lock-handoff.md`) states that no independently enforced exclusive freeze/main-lock proof or separately reviewed one-shot action authority has been supplied. `docs/phase8a-2023-run385-immutable-tag-feasibility.md` separately confirms the installed three-job workflow **rejects tag refs**, so substituting an unverified tag into dispatch cannot solve the ref/SHA problem.

The extensive generated PUBLIC source+named-parent inotify regressions #1485–#1522 establish native observation limits, including real MAP_SHARED data writes without IN_MODIFY, original inode lifetime after pathname unlink and FD close, and kernel-assisted copies/splices. The anonymous generated PUBLIC memfd regressions #1523–#1543 establish that **some specific kernel seals really deny particular syscalls on that different anonymous inode**, but also that future-write seals leave previously writable mappings live, single-purpose seals leave other mutation paths, a sealed source can still be read and its data copied to a different destination, and even a full content/size seal does not freeze inode permission metadata. **None of this proves an independently enforced rule over the actual protected annual filesystem source.**

## Gate A — Independent OS-enforced protected-source no-write (DEC-650 / #820)

A future qualified reviewer must obtain and sign **independent evidence**, outside the proposed annual job's own writable control plane, before any no-write claim can become eligible:

| Required proof | Acceptance criterion | Fail-closed counterexample |
| --- | --- | --- |
| Actual protected object identity | Authenticate precisely which original protected annual source object(s) are covered, including canonical source provenance, content hashes, inode/mount identity where appropriate, all aliases and the full execution-time reference path | A similarly named PUBLIC fixture, sealed anonymous memfd, renamed pathname, hard link or replica passes while the protected original remains writable |
| Mechanism and trust separation | Show the *deployed* OS/storage permission or immutability rule, configured by an independently authorized control owner and not bypassable by executor credentials, inherited handles, alternate namespaces/mounts or higher-privilege actors in the approved threat model | A process retains O_RDWR, MAP_SHARED, procfd alias or other writable path despite a later chmod/read-only observation |
| Live scope/lifetime | Prove the protected rule is effective **before first protected checkout/read/access** and persists for the complete authorized evidence window, with independently timestamped and authenticated start/end proof | A read-only flag observed after preflight, only on one namespace, or only before an administrator unmount/change |
| Mandatory denied-operation tests | In an approved disposable **same-policy representative** environment, independently demonstrate expected denials of write, truncate, fallocate hole/zero, writable mappings including existing mappings, procfd reopening, renames/aliases and other applicable data-mutating routes; retain exact kernel errno and unchanged original-object bytes | An O_RDONLY ftruncate rejection is mistaken for a system-wide denial; file length/bytes change without IN_MODIFY |
| Tamper/bypass resistance | Separately authenticate effective administrator/ruleset privileges, no-bypass authorizations, access revocation/handle closure strategy, audit trail and response to loss/ambiguity | A writable privileged actor or cached writable mapping survives a supposed exclusive write freeze |
| Independent decision authority | A qualified non-executor reviewer signs exact source, policy, window, method, negative probes and review decision; no script, local checksum, inotify event or test count may self-authorize | `independent_os_proof_verified` inferred from generated PUBLIC success or a matching SHA computed by the same actor |

**No candidate architecture is selected, installed or asserted to work here.** A read-only mount, immutable external storage, access policy or sealing approach is at most a separately reviewable proposal until the entire actual protected-object and bypass/lifetime proof passes. Credentials and bypass tokens must never be printed, checked in, or used to weaken an installed runner.

## Gate B — Exclusive immutable one-shot annual run385 admission (DEC-651 / #821 / #779)

| Stage | Independently required check | Failure disposition |
| --- | --- | --- |
| Before job/checkout | Authenticated exclusive workflow/event/ref/repository/**reviewed resolved SHA** source of truth, invariant across the server-side dispatch transaction; effective no-bypass lock or separately installed audited immutable-tag architecture | **BLOCKED**. A mutable branch pointer or ordinary mutable tag is insufficient |
| Before package install and runnable code | Enforced step ordering and job admission on **all three** preflight, 18-cell matrix and freeze paths; exact reviewed workflow/runtime/blob identity checked *before* any setup/install or protected evidence/API fetch | **BLOCKED** if checks occur after checkout, install or evidence metadata access |
| Before first evidence byte | Reverify the same independently approved ref/SHA/workflow/runtime identity, protected no-write lifetime and source provenance; disallow in-band self-supplied expected SHA | **BLOCKED** if any API, archive, manifest or source is accessed before authorization |
| Unique annual slot | Fresh independent run inventory and predecessor evidence must prove the one permitted 2023 slot **run385 attempt1** remains unconsumed; obtain new narrowly scoped one-shot action decision separate from review of any draft | **BLOCKED** on unknown state, race, unavailable inventory or altered predecessor |
| After dispatch (only if separately authorized later) | Bind observed result to exactly the approved commit, workflow, unique run number/attempt and intended matrix outputs; independently verify expected immutable evidence before any downstream decision | On failure/ambiguity, terminal hold: **no rerun, retry, replacement or attempt2** |
| Trading boundary | No annual catalogue testing, source write authorization, strategy promotion, brokerage, demo/live orders or real-money trading follows from passing tests/CI/admission alone | Every execution/trading authority remains **false** unless separately and expressly authorized |

## Status and artifact classification

- Every existing #1543-and-earlier draft remains draft and **NEVER MERGE / NEVER PROMOTE**. Future commits are one-commit descendants and individually require completed exact-head **Phase3 AND full historical `tests` CI** plus qualified independent security review. Historical failed exact SHAs remain failed; only a new forward-only repair may establish a new verified head.
- All generated PUBLIC filesystem and anonymous memfd tests are **diagnostic negative or capability evidence**, not the actual Gate A or Gate B proof. Any newly created reviewer checklist, matrix, SHA digest or test artifact remains nonauthorizing.
- Gate A **DEC-650/#820 remains BLOCKED** and Gate B **DEC-651/#821/#779 remains BLOCKED**. No future release/annual dispatch action is requested or implied here. The user/operator would need an entirely new, separately approved security-control implementation and reviewed one-shot decision after both real gates pass.

**Hard exclusions:** Never protected annual source/evidence access, protected run/test/retry/rerun/dispatch, workflow/ruleset/permission installation or relaxation, broker/trading, mergers or promotions from this draft.
