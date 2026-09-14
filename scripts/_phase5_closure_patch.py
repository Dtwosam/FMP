from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


# Decision log: add active index entry and append the acceptance decision.
decision_path = Path("docs/decision-log.md")
decision = decision_path.read_text(encoding="utf-8")
if "## DEC-030 — Phase 5 leakage-safe feature-engine acceptance review" in decision:
    raise SystemExit("DEC-030 already present")
decision = replace_once(
    decision,
    "- DEC-029 — Phase 5 leakage-safe feature-engine protocol — APPROVED\n",
    "- DEC-029 — Phase 5 leakage-safe feature-engine protocol — APPROVED\n"
    "- DEC-030 — Phase 5 leakage-safe feature-engine acceptance review — APPROVED\n",
    "decision index",
)
decision = decision.rstrip() + """


## DEC-030 — Phase 5 leakage-safe feature-engine acceptance review

**Date:** 2026-09-15
**Status:** APPROVED

Phase 5 is accepted as PASS under DEC-029 and the build-order acceptance gate. The authoritative manual source-free `phase5-features` run `34910227756` executed on exact merged implementation SHA `74dce1b945ad31a05416a4fc9e63443a884cb90c`; all 9/9 EURUSD/GBPUSD/USDJPY × 5m/15m/1h cells succeeded. Each cell verified the accepted Phase 2 artifact and processed-manifest identity, regenerated `fmp-feature-v1` twice deterministically, verified locked pre-2024 coverage, and uploaded evidence.

Independent inspection of all nine evidence ZIPs verified 9/9 ZIP digests, 972/972 monthly Parquet SHA/size/footer-row-count records, exact 55-column schema agreement, 108 source months per cell from 2015-01 through 2023-12, 48 feature fields/null-count entries, no 1m outputs, no 2024+ output paths, and zero audit errors. Total accepted rows are 4,023,279. The merged-main implementation regression and unchanged Phase 3 acceptance runs `34910118880` and `34910118886` both succeeded.

Consequences: Phase 5 is formally PASS. Checkpoint `fmp-v1-phase5-features` is to be created at the verified merged acceptance-closure commit after post-merge source-free regression checks succeed. Phase 6 remains UNSTARTED and unauthorized until a separate approved design/implementation decision. The final untouched 2024-01-01 through 2026-08-20 test period remains locked; broker/live/demo integration and real-money trading remain locked; DEC-008 remains unchanged. Detailed evidence is in `docs/phase5-acceptance-evidence.md`.
"""
decision_path.write_text(decision, encoding="utf-8")


# Project state: advance only Phase 5 to PASS, keep every later gate locked.
state_path = Path("docs/project-state.md")
state = state_path.read_text(encoding="utf-8")
state = replace_once(state, "**Updated:** 2026-09-14", "**Updated:** 2026-09-15", "state date")
state = replace_once(state, "**Phase status:** ACTIVE", "**Phase status:** PASS", "phase status")
state = replace_once(
    state,
    "**Next milestone:** Implement and verify `fmp-feature-v1` under DEC-029; final-test data remains locked and 2024+ processed partitions are not readable by normal Phase 5 tooling",
    "**Next milestone:** Record the verified Phase 5 checkpoint; Phase 6 remains UNSTARTED and final-test data remains locked",
    "next milestone",
)
marker = "## Phase 5 — ACTIVE"
if state.count(marker) != 1:
    raise SystemExit(f"Phase 5 ACTIVE marker expected once, found {state.count(marker)}")
state = state.split(marker, 1)[0].rstrip() + """


## Phase 5 — PASS

DEC-029 freezes the leakage-safe `fmp-feature-v1` protocol; DEC-030 records the Phase 5 acceptance review.

- implementation merge: `74dce1b945ad31a05416a4fc9e63443a884cb90c`
- merged-main tests: run `34910118880` — SUCCESS
- unchanged Phase 3 acceptance: run `34910118886` — SUCCESS
- authoritative feature generation: run `34910227756` — SUCCESS
- matrix: 3 pairs × 3 timeframes = 9/9 cells successful
- independent evidence audit: 9/9 ZIP digests and 972/972 monthly Parquet partitions verified with zero validation errors
- total accepted feature rows: 4,023,279
- source coverage: 2015-01-01 through 2023-12-31 only
- feature schema: `fmp-feature-v1`, 55 columns = 7 identity + 48 feature values
- Final-test touched: NO
- checkpoint: `fmp-v1-phase5-features` — PENDING post-merge verification

Phase 5 is formally PASS under DEC-030. Normal Phase 5 tooling still rejects any processed source request reaching 2024-01-01 or later before that partition is opened. The final-test period remains locked.

## Phase 6 — UNSTARTED

Phase 6 model fitting and statistical/ML experiments remain unauthorized pending a separate explicitly approved design and implementation gate. No labels, models, final-test access, broker/live/demo integration, or candidate retuning is authorized by Phase 5 acceptance. Broker/live/demo integration and real-money trading remain locked; DEC-008 remains unchanged.
"""
state_path.write_text(state, encoding="utf-8")


# Historical state guards: update only assertions made stale by the Phase 5 closure.
updates = {
    "tests/test_phase4_acceptance_state.py": [
        ("self.assertIn(\"**Phase status:** ACTIVE\", state)", "self.assertIn(\"**Phase status:** PASS\", state)"),
        ("self.assertIn(\"## Phase 5 — ACTIVE\", state)", "self.assertIn(\"## Phase 5 — PASS\", state)"),
    ],
    "tests/test_phase4_checkpoint_state.py": [
        ("self.assertIn(\"## Phase 5 — ACTIVE\", state)", "self.assertIn(\"## Phase 5 — PASS\", state)"),
    ],
    "tests/test_phase5_feature_protocol_state.py": [
        ("self.assertIn(\"**Phase status:** ACTIVE\", state)", "self.assertIn(\"**Phase status:** PASS\", state)"),
        ("self.assertIn(\"## Phase 5 — ACTIVE\", state)", "self.assertIn(\"## Phase 5 — PASS\", state)"),
    ],
}
for filename, replacements in updates.items():
    path = Path(filename)
    text = path.read_text(encoding="utf-8")
    for old, new in replacements:
        if old not in text:
            raise SystemExit(f"{filename}: missing expected stale assertion {old!r}")
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
