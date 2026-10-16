"""DEC-1373 inspect committed freeze-source hashing, not historical data.

Source-only AST inspection. Never import/execute annual freeze code, access
protected objects, contact GitHub Actions or install security controls.
"""
from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    "HEAD:src/fmp/discovery/"
    "annual_pattern_catalogue_segment_evidence.py"
)


class AnnualFreezeFingerprintIsContentDigestNotExternalAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = subprocess.check_output(
            ["git", "show", SOURCE], cwd=ROOT, text=True
        )
        module = ast.parse(cls.text)
        cls.functions = {
            n.name: ast.get_source_segment(cls.text, n)
            for n in module.body if isinstance(n, ast.FunctionDef)
        }

    def test_freeze_json_canonicalization_is_local_serialization(self):
        s = self.functions["_canonical_json"]
        self.assertIn("sort_keys=True", s)
        self.assertIn("allow_nan=False", s)
        self.assertIn('.encode("utf-8")', s)

    def test_digest_uses_standard_sha256_of_caller_value(self):
        s = self.functions["_sha256_bytes"]
        self.assertIn("hashlib.sha256(value).hexdigest()", s)

    def test_sha_validator_checks_format_not_independent_signer(self):
        s = self.functions["_validate_sha256"]
        self.assertIn("len(value) != 64", s)
        self.assertIn("int(value, 16)", s)
        self.assertIn("return value", s)

    def test_commit_validator_enforces_forty_hex_shape_not_external_sha(self):
        s = self.functions["_validate_commit"]
        self.assertIn("len(value) != 40", s)
        self.assertIn("int(value, 16)", s)
        self.assertIn("return value.lower()", s)

    def test_compiler_fingerprints_its_own_evidence_mapping(self):
        s = self.functions["compile_annual_segment_freeze"]
        self.assertIn(
            'evidence["evidence_fingerprint"] = _sha256_bytes(_canonical_json(evidence))',
            s)
        self.assertIn("validate_annual_segment_freeze(evidence, expected_summaries=ordered)", s)

    def test_validator_rehashes_unsigned_evidence_internally(self):
        s = self.functions["validate_annual_segment_freeze"]
        self.assertIn('unsigned.pop("evidence_fingerprint", None)', s)
        self.assertIn(
            "if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:", s)
        self.assertIn("raise ValueError", s)

    def test_external_expected_summaries_are_optional_to_validator(self):
        s = self.functions["validate_annual_segment_freeze"]
        self.assertIn("expected_summaries: Sequence[ValidatedAnnualCellSummary] | None = None", s)
        self.assertIn("if expected_summaries is not None:", s)

    def test_validator_checks_cell_universe_identity_and_code_commit(self):
        s = self.functions["validate_annual_segment_freeze"]
        for needle in (
            "len(raw_cells) != EXPECTED_CELLS_PER_SEGMENT",
            "if identities != list(expected):",
            "if any(item.code_commit != code_commit for item in summaries):",
        ):
            self.assertIn(needle, s)

    def test_output_authorization_flags_remain_false(self):
        for name in (
            "HISTORICAL_ARTIFACT_READ_AUTHORIZED", "HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED",
            "STRATEGY_V1_SYNTHESIS_AUTHORIZED", "PROMOTION_AUTHORIZED",
            "BROKER_MUTATION_AUTHORIZED", "TRADING_AUTHORIZED",
        ):
            with self.subTest(name=name):
                self.assertIn(name + " = False", self.text)
        self.assertIn("if value.get(field) is not False:", 
                      self.functions["validate_annual_segment_freeze"])
