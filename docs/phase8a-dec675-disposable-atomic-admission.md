# DEC-675 — Disposable SQLite one-shot admission model

**DRAFT / NEVER MERGE · Research-only · Not a GitHub Actions dispatcher.**

This is a local, deterministic engineering rehearsal for DEC-651 / issue #779. It does **not** contact GitHub, change any workflow/ref/policy, run the protected annual job, or touch external systems. Its only database is a newly created SQLite file in a private temporary directory rooted at fixed /tmp. The code has **no GitHub API client, network import, workflow dispatch code, credential input or user-selected filesystem destination**.

## Local concurrency behavior

The model allocates one **synthetic, nonauthoritative** slot identified by dec675_disposable_slot_only. Its approved SHA (aaaa...), actor (local_synthetic_actor) and payload (public_fake_payload) are constants, not real annual values. It initializes the SQLite database with O_CREAT|O_EXCL|O_NOFOLLOW so it cannot overwrite a previous ledger; the claim path uses mode=rw so a missing database cannot be silently recreated.

Each simulated claimant uses an independent SQLite connection and BEGIN IMMEDIATE, then conditionally updates the slot from UNCLAIMED to RESERVED only if its source, actor and payload match. A replay, wrong actor/input or second claimant returns BLOCKED. The reserved state persists across simulated process restart and cannot be reset through the public claim function.

A disposable opt-in demo runs 24 simultaneous **threads** against the same fake ledger, requires exactly one successful simulated reservation, rejects all remaining 23 contenders, verifies persisted state and refuses a post-reservation replay. The regression suite also races six independent **processes** and requires a single winner. Its 17 source-defined tests passed in a local run.

Default inert CLI:

    python -B scripts/dec675_synthetic_atomic_admission.py

Explicit temporary simulation:

    python -B scripts/dec675_synthetic_atomic_admission.py --execute-disposable-demo

CLI returns only BLOCKED (exit **2**) or LOCAL_DISPOSABLE_WITNESS_UNVERIFIED (exit **3**). An internal _claim returns SYNTHETIC_RESERVATION_UNVERIFIED as a test-only event. **No state or return code grants any real dispatch authority**; every outcome includes can_authorize_dispatch=false, server_enforcement_verified=false, annual_run_385_consumed=false.

## DEC-676 — Terminal ambiguous handoff before any hypothetical transport

The base DEC-675 model stops at an atomic local RESERVED slot. That prevents a second ordinary local claimant, but does not explicitly represent **uncertainty around delivery of a future one-shot remote request**. This stacked source-only revision adds a terminal HANDOFF_UNKNOWN state. The helper changes exactly one matching RESERVED claim to HANDOFF_UNKNOWN under BEGIN IMMEDIATE and commits it **before any possible external side effect**. The research tool has **NO remote transport code or supplied callback**.

Once marked unknown, the same claimant, another claimant, a caller with a different claim ID, or a restarted local process cannot replay or reset the slot through the public API. Missing/wrong claim IDs and handoff requests prior to a reservation return BLOCKED. The fake 24-thread demo now asserts persistence of this terminal uncertainty, a blocked second handoff, and blocked replay. There is no route to DISPATCHED, DELIVERED, safe retry or actual workflow authorization.

Six added regression cases bring the defined suite to **23 tests**. Local testing passed all 23, including process-level race cases and the earlier direct-ledger-tampering negative control. The latter remains decisive: **a privileged SQLite writer can reset state directly**. Therefore HANDOFF_UNKNOWN is a toy protocol state, not a tamper-proof server-side ledger, an authenticated remote receipt or a GitHub workflow admission gate.

An actual external operation may be delivered despite a lost acknowledgment, or fail before delivery. This model cannot distinguish those cases, and does not submit a request to find out. Under the real DEC-651 acceptance contract, a run-385 result cannot be retried on ambiguity without a separately reviewed and explicitly authorized protocol. This draft grants no such permission.

## Explicit negative proof: same-user ledger tampering

One adversarial unit test directly changes the local SQLite row from RESERVED back to UNCLAIMED using a separate writable connection. A subsequent synthetic claim can reserve again. This **deliberately demonstrates that SQLite concurrency safety is NOT a security boundary against a ledger owner or privileged actor**. The test still verifies both authorization flags false.

Thus even if the local SQLite concurrency model passes, it cannot authenticate a real GitHub ref, control Actions-write identities, exclude administrators, guarantee a durable remote reservation, handle ambiguous dispatch delivery, prevent privileged ledger mutation, or couple reservation atomically to GitHub's run-number allocation. A real run 385 must **never** be submitted on the basis of this model. A crash after local reservation leaves a fail-stop, non-retryable synthetic slot, not permission to retry remotely.

## Independent acceptance gates still open

- DEC-651 draft #821 and issue #779: independently reviewed and **server-enforced** immutable source/ref, bypass principal census, exclusive dispatch identity, atomic one-shot admission and ambiguity handling.
- DEC-650 draft #820: independent OS-enforced filesystem/credential/network and trusted uploader proofs for the actual preflight + 18 matrix cells + freeze, not a disposable simulation.
- Qualified independent source/security review of this exact commit and current exact-head Phase 3/full regression.

**DRAFT / NEVER MERGE.** No annual run 385 dispatch/test/retry/rerun, protected annual artifact access, main/refs/workflow/ruleset/permission/runner mutations, broker or trading activities.
