# DEC-646 — Same-UID and mount-boundary negative evidence (DRAFT / NEVER MERGE)

This is a **source-only eight-test and documentation experiment** stacked on [DEC-645 #815](https://github.com/Dtwosam/FMP/pull/815). It changes no executable trading/audit code, 23 assess-only CLI wrappers, shared external report helper, installed GitHub workflow, original PR, broker, credentials, historical data or annual run385 state. Every filesystem write exercised by these tests is confined to disposable synthetic directories under `tempfile.TemporaryDirectory` (plus an optional disposable `/dev/shm` fixture).

## Why ordinary permission flags are insufficient

1. In a synthetic checkout directory owned by the test's same Unix UID, setting directory mode `0555` removes write mode bits, but **the owner may chmod it back to `0755`**, then rename a previously external report directory into checkout. `chmod -R a-w` is therefore **not** a security boundary against a same-UID actor who owns checkout. This proves a scoped permission-model limitation, not a real repository compromise.
2. A path's `stat()` permission snapshot can change. Directory descriptors pin inodes but do **not** freeze their namespace location: after rename into synthetic checkout, descriptor-relative `os.open(...,dir_fd=...)` creates a report in the newly located directory. A read-only token, static mode-bit snapshot, or final `realpath()` does not eliminate races.
3. Optional Linux disposable cross-filesystem fixture (`/dev/shm` versus TemporaryDirectory) expects `EXDEV` when moving a directory across differing devices. This supports investigating mount-separated execution, but is **not evidence of FMP runner mount/namespace isolation**. The test skips if an appropriate cross-device fixture is unavailable.
4. The previously authored DEC-645 mount diagnostic remains non-authorizing even with a same-device writable pair. It always returns `authorized=false`; observational metadata is not a substitute for OS access controls.
5. A frozen-main annual-workflow source check verifies three `actions/checkout@v6` jobs on `ubuntu-latest`, with read-only token permissions and **no explicitly declared read-only checkout mount** in that YAML. This is a negative current-source observation, not proof about every implicit host security policy.

## Offline checks

Run `python -B -m unittest -v tests/test_phase8a_annual_pattern_catalogue_2023_dec646_permission_boundary_counterexamples.py` in a checkout of this preview. The eight tests passed **8/8 locally**, with no annual workflows dispatched and no changes to any real checkout. Only GitHub's exact-source-merge CI and independent review may establish repository regression compatibility.

## Explicit blocking conditions

An adversary capable of writing/reparenting into checkout can violate an unconditional checkout-inventory guarantee even after DEC-643 descriptor anchoring. To enforce that guarantee, establish the actual threat model and externally enforced checkout mount, namespace, UID/ownership and writable-alias constraints **in every relevant job**; do not rely on a user-owned chmod snapshot or read-only GitHub API token. #813 is technically green but security-blocked; #814's green negative regression deliberately reproduces the remaining weakness. A distinct mount does not imply no privileged remount, and a read-only mount probe is not an execution gate.

All ancestor #809–815 and this #816 remain **DRAFT / NEVER MERGE**. Original PRs #796–800 lack independent review; main is unprotected with no rulesets at last read; annual run385 remains unconsumed and blocked. No changes to branch protection, tags, workflow dispatch/retry, protected data, broker or trading.