# Phase 8A — EXP-062 Runtime Gate-Proof Evidence Freeze

**Date:** 2026-09-28  
**Status:** REVIEWED RUNTIME EVIDENCE BOUND / HISTORICAL SLOT STILL CLOSED  
**Decision:** DEC-306  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-301, DEC-303, DEC-304, DEC-305

## Purpose

DEC-306 binds the actual successful DEC-303 one-shot executor and the actual
fail-closed EXP-062 gate proof to immutable GitHub run/artifact identities and
downloaded evidence hashes.

DEC-305 remains the generic deterministic freeze builder. DEC-306 is the concrete
runtime freeze for the evidence GitHub actually produced.

## Frozen executor evidence

The authoritative executor is:

- run id: `36358278933`;
- workflow: `phase8a-exp062-proof-one-shot-execute`;
- head: `f2c55ac36a1a9ba7596ec0d4559c877a66cda0fb`;
- run number / attempt: `1 / 1`;
- terminal conclusion: `success`;
- dispatch-evidence artifact id: `10944404609`;
- artifact digest:
  `sha256:f1baf1e77100cb314b1e573a404508d379a569ffadea2f702bfdaebfad2c3f64`.

The executor passed its exact-main, first-run, zero-proof-history, two-fresh-plan,
single-dispatch, and post-dispatch verification gates.

## Frozen proof evidence

The authoritative EXP-062 proof is:

- run id: `36358289723`;
- workflow: `phase8a-exp062-discovery`;
- head: `f2c55ac36a1a9ba7596ec0d4559c877a66cda0fb`;
- run number / attempt: `1 / 1`;
- terminal conclusion: `failure`;
- preflight job id `108730271344`: failed at the still-locked historical execution gate;
- skipped matrix-placeholder job id `108730343578`;
- skipped aggregate job id `108730343797`;
- preflight artifact id: `10943489995`;
- preflight artifact digest:
  `sha256:0cc405cc6d8b5941f7051e7907e2a7040a21a05411b29774ebbcd3884da9193f`.

There are zero cell-result artifacts and zero aggregate-result artifacts.

## Downloaded evidence hashes

DEC-306 freezes both raw and canonical evidence identities:

- executor raw:
  `64e8bfca0f7b5ae8814ec58c1dd7725c6b161276ec28ceacfc0ad0bc7c9483a1`;
- executor canonical:
  `1f7a90442cdfd587b66cb209625fbb2a4261ec1296f228663ed7bb7118320507`;
- proof-run raw:
  `a8926d829bffb87f3efb88dd6b5a35aa2baa59af919476dab21d592a3baac703`;
- proof-run canonical:
  `0e1d8cf042fbeb2b50842ed22a96df6aa62ebec8eab7460c96dae4ee41d45fca`;
- proof-inventory raw:
  `0e7b74527b17db5b27ce38e3bc7d26d2ef12ac2e5171170dca92c1844f209524`;
- proof-inventory canonical:
  `cf67da5ce88e075aed7a22168e547ac788e11144946d5b8e7d7f2209f9558b51`;
- preflight raw:
  `c9554dead93a0c9657a6e9f1ad18b43520bcd8ea7f0466e9f5f9f7a0bc6a7b43`;
- preflight canonical:
  `7c2456ce11639a23715d5c07fd28976e54631056e30d01691ef8f7cd822e100b`;
- preflight source fingerprint:
  `6110876b9d2f620c780ee8952115dc6841c9269d89c6ca45d8e0c6d59ba32b3d`.

The executor artifact's `executor.json` contains the dispatched run URL as a first
line before its JSON object. DEC-306 therefore binds the raw file hash as well as the
canonical parsed JSON hash rather than hiding that representation detail.

## DEC-305 binding

The reviewed DEC-305 freeze fingerprint is:

`fadd6e512b95179fa682d05c8550c914db81e559d9c0ad8da0bedb03bb43a096`.

DEC-306 requires this exact fingerprint and rechecks that every authority-negative
field remains false.

## Redundant bootstrap run

PR #448 later caused executor workflow run `36360111479`, run number 2 / attempt 1.
It failed at the first-run guard before Python setup, dispatch, or proof submission.
It is not an authoritative executor and created no second EXP-062 proof. This
fail-closed run does not consume any historical-result slot.

## Safety boundary

DEC-306 opens no historical-result slot. Historical-result dispatch/execution,
discovery-result production, rerun/retry/replacement, reserved 2023-2026 access,
candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and trading
all remain false.

The next safe gate is a separate source-only one-slot historical-run authorization
contract for the unchanged 2015-2022 research window.
