# Phase 8A — EXP-061 Gate-Proof Terminal Contract

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY PROOF CONTRACT / NO DISPATCH AUTHORIZED  
**Decision:** DEC-277  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-276

## 1. Purpose

DEC-277 defines how to review a future proof-only run of the active EXP-061 workflow.

The proof is not a historical discovery run. Its only purpose is to demonstrate that the installed workflow cannot pass the DEC-275 execution gate.

DEC-277 authorizes no dispatch.

## 2. Expected proof run

A later authorization must bind an exact merged-main head. For that head, the proof expects:

- workflow name `phase8a-exp061-discovery`;
- path `.github/workflows/phase8a-exp061-discovery.yml`;
- event `workflow_dispatch`;
- branch `main`;
- run attempt `1`;
- terminal status `completed`;
- terminal conclusion `failure`.

The failure is expected and required.

## 3. Job semantics

The proof requires exactly one materialized preflight job named:

`exp061-preflight`

with conclusion `failure`.

GitHub may or may not materialize every downstream skipped matrix child after a failed dependency. DEC-277 therefore does not require all 18 skipped cell rows to appear in the jobs API.

Any downstream job that does materialize must:

- have one of the exact DEC-274 cell/aggregate display names;
- be terminal;
- conclude `skipped`.

Any downstream `success`, `failure`, `cancelled`, or active state invalidates the proof.

## 4. Artifact semantics

The proof requires exactly one non-expired artifact:

`phase8a-exp061-preflight-<proof-head-sha>`.

No cell artifact and no aggregate artifact may exist.

The preflight artifact must contain the exact DEC-275 preflight JSON for the proof head.

## 5. Preflight evidence semantics

The preflight evidence must prove:

- exact DEC-275 source decision/version;
- accepted EXP-044 feature/outcome run identities;
- exact aggregate source-evidence artifact identities;
- exactly nine verified pair/timeframe source pairs;
- `source_ready=true`;
- exact proof commit;
- exact deterministic DEC-275 workflow-source payload for that commit;
- intact source fingerprint;
- all historical/result/trading authorization flags false.

## 6. Slot semantics

A valid proof:

- does not consume the future historical-result slot;
- does not authorize historical discovery;
- does not create a discovery result;
- does not authorize retry/rerun/replacement of a historical result run;
- does not open reserved 2023-2026 data;
- does not authorize candidate compilation, Phase 8B, demo, broker mutation, live orders, real-money action, or trading.

## 7. Frozen implementation identities

- proof contract: `src/fmp/discovery/proof_contract.py`;
- proof-contract blob: `1a2b6c404cba4e1f6e9b28d46a0671a6a318e48a`;
- focused tests: `tests/test_phase8a_exp061_gate_proof_contract.py`;
- focused-test blob: `bd4f837c99090bcabc1ef8932b39653dc1d137e5`.

## 8. Next gate

After DEC-277 merges green and DEC-276 is installed on merged `main`, a later decision may bind the exact merged-main head, verify no prior proof run exists for that head, and authorize exactly one proof-only dispatch.

That authorization must still keep historical discovery/result execution false.
