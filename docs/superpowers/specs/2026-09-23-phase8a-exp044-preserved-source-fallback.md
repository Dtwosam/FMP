# Phase 8A — EXP-044 Preserved Phase 2 Source Fallback

**Date:** 2026-09-23  
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN  
**Decision:** DEC-085  
**Experiment:** EXP-20260923-044

## 1. Purpose

DEC-084 preserves exact accepted Phase 2 ZIP bytes as a GitHub release, but the EXP-044 feature/outcome workflows still consumed only the original time-limited Actions artifacts.

DEC-085 adds an exact-byte fallback so EXP-044 can continue after Actions artifact expiry without reacquiring Dukascopy data or changing any accepted source identity.

## 2. One source mode per run

Source availability is resolved for the complete EURUSD / GBPUSD / USDJPY bundle.

The only allowed run-wide modes are:

- `actions`: all three original Actions artifacts pass DEC-078 identity/lifetime checks;
- `release`: the complete published DEC-084 preservation release and manifest validate exactly.

Mixed source modes are not allowed.

If even one original Actions artifact is not ready, the resolver does not combine remaining Actions artifacts with release assets. It requires the complete verified release bundle for all three symbols.

## 3. Actions mode remains preferred

The resolver first runs the existing DEC-078 source preflight over the exact original Actions metadata.

When all three originals pass:

- `source_mode=actions`;
- the preservation release is not required;
- the original Actions IDs/run/head remain the download source.

This preserves current behavior while the original artifacts are healthy.

## 4. Release fallback requirements

Release mode requires both:

- the published release `fmp-phase2-accepted-artifacts-v1`;
- its exact `phase2-preservation-manifest.json`.

The preservation manifest must revalidate:

- EXP-044 identity;
- Dukascopy historical source;
- Phase 2 source run/head;
- exact original Actions artifact IDs/names;
- exact release asset names;
- exact ZIP SHA-256 identities;
- exact ZIP byte sizes;
- exact processed-manifest SHA-256 identities;
- no new acquisition;
- unchanged source bytes;
- all model/trading authorization flags false.

The published release must be non-draft, non-prerelease, contain exactly the three ZIPs plus preservation manifest, and expose the exact frozen ZIP sizes/digests.

## 5. Workflow source availability output

Both authoritative EXP-044 workflows now run the same source-availability resolver before heavy work.

The preflight emits one `source_mode` output.

Each of the three pair jobs receives that same mode.

## 6. Pair download behavior

For `actions` mode, each pair job downloads the original frozen Actions artifact.

For `release` mode, each pair job downloads the exact corresponding DEC-084 release asset.

Regardless of mode, every pair job independently rechecks:

- exact ZIP byte size;
- exact ZIP SHA-256;
- exact embedded processed-manifest SHA-256

before feature generation or outcome materialization.

The downstream dataset root is identical after extraction.

## 7. Operator behavior

The local DEC-081/082/083/084 operator is aligned with the same source-resolution rules.

- `preserve-phase2` remains strict: it requires the original Actions artifacts because its purpose is to preserve those originals.
- `features` and `outcomes` prefer the original Actions bundle but may use the complete validated release bundle when needed.
- `readiness` remains read-only and unchanged.

## 8. Research boundary

DEC-085 does not define a new dataset.

Release mode is authorized only because the release ZIP bytes must match the exact Phase 2 ZIP hashes and embedded manifest identities already accepted.

DEC-085 does not authorize:

- different or partially matching release bytes;
- fresh Dukascopy acquisition;
- mixed Actions/release runs;
- altered processed manifests;
- model fitting;
- promotion;
- shadow/demo/broker/live/real-money actions.

## 9. Next gate

While the original Actions artifacts remain healthy, the preferred sequence is still:

1. execute DEC-084 preservation;
2. dispatch EXP-044 feature generation;
3. verify feature evidence;
4. dispatch outcomes;
5. inspect DEC-074 readiness through DEC-083.

If the Actions artifacts later become unavailable, the same feature/outcome workflows may proceed only through the exact DEC-085 release fallback.
