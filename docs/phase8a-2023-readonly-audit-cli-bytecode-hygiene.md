# DEC-627 — Read-only offline annual audit CLI bytecode hygiene

**Status: SOURCE-ONLY / NO LIVE WORKFLOW OR RUNTIME AMENDMENT / NO DISPATCH OR TRADING AUTHORITY.**

## Failure mode discovered by independent review

DEC-625 PR #794 received a P2 independent-review finding: its assess-only CLI could import the `fmp` package and emit `src/fmp/**/__pycache__/*.pyc` files inside the checkout **before** checking that `--out` was outside the checkout. The output-path guard alone therefore cannot enforce a strict read-only CLI.

DEC-625 and DEC-626 separately introduced `sys.dont_write_bytecode = True` **before** importing any `fmp` module, plus real clean-checkout subprocess tests. This DEC-627 change applies the same small import-time guard to **11 previously merged assess-only audit CLIs**:

- `main_lock_readiness`
- `immutable_tag_feasibility`
- `tag_ruleset_static_review`
- `tag_ref_guard_rehearsal`
- `disarmed_tag_amendment_preview`
- `ref_race_interleaving_model`
- `lock_witness_coverage`
- `ambiguous_dispatch_hold_model`
- `runtime_tag_sha_binding_preview`
- `preaccess_identity_gate_topology_audit`
- `three_layer_admission_model`

These are exclusively offline audit/report surfaces. This change **does not alter** annual research dispatch CLIs, workflow or installed 2023 authorization runtime, tag/ruleset/branch protection, broker/execution logic, or research results. It adds no Python dependencies.

## Exact test

The focused DEC-627 unit test copies the actual `src/fmp` package without caches and all 11 CLI scripts into a temporary checkout. It clears `PYTHONDONTWRITEBYTECODE` and `PYTHONPYCACHEPREFIX` in the subprocess environment, invokes each script with `--help` (which loads its imported modules but does not run any research or API action), and checks that:

1. each process terminates successfully and exposes its single `assess` subcommand;
2. the copied checkout's file inventory remains exactly unchanged after each process;
3. no `*.pyc` appears anywhere in the checkout; and
4. each script sets the bytecode-write suppression **before** its first `fmp.discovery` import.

This test is deliberately limited to import-time bytecode hygiene. It does not pretend to prove that every future CLI branch, OS file operation or external dependency is read-only. More importantly, a no-write CLI still does not authenticate any review, tag, admin lock or GitHub context.

## Unchanged security restrictions

Issue #779 remains OPEN. 2023 research run 385/attempt 1 remains reserved, and external continuously authenticated no-bypass administrator immutable-ref protection, independently reviewed ref/SHA identity, an explicitly approved installed three-job workflow/runtime amendment, fresh run inventory and one-shot action are still missing. No research dispatch/retry, historical protected read, next annual year, promotion, demo/live/real-money order or trading is authorized by DEC-627.
