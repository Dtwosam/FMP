from pathlib import Path

MERGE_SHA = "115bb8080e951db16ca1a1174227ffa181a03d1b"
TESTS_RUN = "34903338560"
PHASE3_RUN = "34903338538"
TAG = "fmp-v1-phase4-baselines"

# Finalize the acceptance evidence after the verified merge/tag.
evidence_path = Path("docs/phase4-acceptance-evidence.md")
evidence = evidence_path.read_text(encoding="utf-8")
replacements = [
    (
        "**Decision:** DEC-028 — pending acceptance-closure merge",
        "**Decision:** DEC-028 — APPROVED",
    ),
    (
        "**Checkpoint:** `fmp-v1-phase4-baselines` — pending acceptance-closure merge and post-merge verification",
        f"**Checkpoint:** `{TAG}` — CREATED at `{MERGE_SHA}`",
    ),
    (
        "After the acceptance closure is merged and its source-free regression checks pass on `main`, create checkpoint `fmp-v1-phase4-baselines` at the verified closure commit.",
        f"The acceptance closure merged at `{MERGE_SHA}`. Post-merge tests run `{TESTS_RUN}` and Phase 3 acceptance run `{PHASE3_RUN}` both completed SUCCESS, and no Phase 1 acquisition or Phase 4 benchmark reran. Checkpoint `{TAG}` was then created at that verified closure commit.",
    ),
]
for old, new in replacements:
    if evidence.count(old) != 1:
        raise SystemExit(f"acceptance evidence marker mismatch: {old}")
    evidence = evidence.replace(old, new, 1)
evidence_path.write_text(evidence, encoding="utf-8")

# Record the frozen checkpoint in project state without starting Phase 5.
state_path = Path("docs/project-state.md")
state = state_path.read_text(encoding="utf-8")
state_replacements = [
    (
        "**Next milestone:** Create checkpoint `fmp-v1-phase4-baselines` at the verified acceptance-closure commit, then begin a separate Phase 5 leakage-safe feature-engine design; final-test data remains locked",
        "**Next milestone:** Begin a separate Phase 5 leakage-safe feature-engine design from the frozen Phase 4 checkpoint; final-test data remains locked",
    ),
    (
        "Detailed acceptance evidence is `docs/phase4-acceptance-evidence.md`. The final-test period remains locked. Checkpoint `fmp-v1-phase4-baselines` is created only after the merged acceptance closure passes post-merge verification.",
        f"Detailed acceptance evidence is `docs/phase4-acceptance-evidence.md`. The final-test period remains locked. Phase 4 checkpoint: `{TAG}` at `{MERGE_SHA}`; post-merge tests `{TESTS_RUN}` SUCCESS and Phase 3 acceptance `{PHASE3_RUN}` SUCCESS.",
    ),
]
for old, new in state_replacements:
    if state.count(old) != 1:
        raise SystemExit(f"project-state marker mismatch: {old}")
    state = state.replace(old, new, 1)
state_path.write_text(state, encoding="utf-8")

# Guard the frozen checkpoint record and later-phase locks.
test_path = Path("tests/test_phase4_checkpoint_state.py")
test_path.write_text(
    f'''from pathlib import Path\nimport unittest\n\nROOT = Path(__file__).resolve().parents[1]\n\n\nclass Phase4CheckpointStateTests(unittest.TestCase):\n    def test_phase4_checkpoint_is_recorded_without_starting_phase5(self) -> None:\n        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")\n        evidence = (ROOT / "docs/phase4-acceptance-evidence.md").read_text(encoding="utf-8")\n\n        self.assertIn("`{TAG}`", state)\n        self.assertIn("`{MERGE_SHA}`", state)\n        self.assertIn("`{TAG}` — CREATED at `{MERGE_SHA}`", evidence)\n        self.assertIn("**Decision:** DEC-028 — APPROVED", evidence)\n        self.assertIn("tests run `{TESTS_RUN}`", evidence)\n        self.assertIn("Phase 3 acceptance run `{PHASE3_RUN}`", evidence)\n        self.assertIn("## Phase 4 — PASS", state)\n        self.assertIn("## Phase 5 — UNSTARTED", state)\n        self.assertIn("final-test data remains locked", state.lower())\n        self.assertIn("Real-money trading remains locked", state)\n        self.assertNotIn("## Phase 5 — ACTIVE", state)\n\n\nif __name__ == "__main__":\n    unittest.main()\n''',
    encoding="utf-8",
)
