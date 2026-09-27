from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Dec268DiscoveryFirstAmendmentTests(unittest.TestCase):
    def _read(self, path: str) -> str:
        return (ROOT / path).read_text(encoding="utf-8")

    def test_canonical_entry_points_name_dec268_discovery_first_direction(self) -> None:
        agents = self._read("AGENTS.md")
        readme = self._read("README.md")
        state = self._read("docs/project-state.md")
        build = self._read("docs/build-order.md")

        self.assertIn("DEC-268 is the default for new post-DEC-268 strategy research", agents)
        self.assertIn("discovery-first", readme)
        self.assertIn("DEC-268 changes the forward research direction", state)
        self.assertIn("DEC-268 is the governing amendment for new strategy discovery", build)

    def test_six_historical_families_are_benchmarks_not_required_universe(self) -> None:
        agents = self._read("AGENTS.md")
        master = self._read("docs/master-spec.md")
        standard = self._read("docs/research-testing-standard.md")

        self.assertIn(
            "Do not treat the six historical rule families as the required or complete strategy universe",
            agents,
        )
        self.assertIn(
            "they are **not** the required or complete universe for future strategy discovery",
            master,
        )
        self.assertIn(
            "supersedes the requirement that all future strategies must begin from those predefined families",
            standard,
        )

    def test_discovery_is_bounded_and_validation_cannot_redesign_candidate(self) -> None:
        spec = self._read(
            "docs/superpowers/specs/2026-09-27-phase8a-discovery-first-amendment.md"
        )
        standard = self._read("docs/research-testing-standard.md")

        self.assertIn("bounded search budget", spec)
        self.assertIn("multiple-comparison/search-volume accounting", spec)
        self.assertIn(
            "The validation data is not allowed to decide what pattern should have been discovered",
            spec,
        )
        self.assertIn(
            "Validation data is not allowed to redesign the pattern",
            standard,
        )

    def test_demo_learning_requires_new_identity_and_fresh_later_evidence(self) -> None:
        spec = self._read(
            "docs/superpowers/specs/2026-09-27-phase8a-discovery-first-amendment.md"
        )
        master = self._read("docs/master-spec.md")
        standard = self._read("docs/research-testing-standard.md")

        self.assertIn("any material change creates a new immutable challenger version", spec)
        self.assertIn(
            "that data becomes research/training evidence for it",
            spec,
        )
        self.assertIn("later fresh prospective shadow/demo window", spec)
        self.assertIn("new immutable identity", master)
        self.assertIn(
            "that demo window is no longer fresh validation for the new version",
            standard,
        )

    def test_exp015_is_preserved_but_does_not_auto_continue(self) -> None:
        state = self._read("docs/project-state.md")
        decision = self._read("docs/decision-log.md")
        spec = self._read(
            "docs/superpowers/specs/2026-09-27-phase8a-discovery-first-amendment.md"
        )

        self.assertIn("EXP-044 V1 CLOSED", state)
        self.assertIn("36279397331", state)
        self.assertIn("Stage B/C are not automatically authorized", state)
        self.assertIn("36279397331", decision)
        self.assertIn("no automatic continuation into EXP-015 Stage B/C", decision)
        self.assertIn("no EXP-015 retry, rerun, replacement", spec)

    def test_dec268_does_not_authorize_trading(self) -> None:
        decision = self._read("docs/decision-log.md")
        spec = self._read(
            "docs/superpowers/specs/2026-09-27-phase8a-discovery-first-amendment.md"
        )

        self.assertIn("NO TRADING AUTHORIZATION", decision)
        self.assertIn("demo-order submission", decision)
        self.assertIn("real-money action", decision)
        self.assertIn(
            "No historical, shadow, demo, broker, live, real-money, or trading execution is authorized",
            spec,
        )


if __name__ == "__main__":
    unittest.main()
