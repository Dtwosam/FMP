"""DEC-1410: fail-closed, source-only 18-cell annual matrix inventory.

Read the checked-in YAML as text; never dispatch the annual workflow, import
its CLI, download artifacts, or touch protected sources. This is not YAML
evaluation or proof of immutable, externally authorized evidence.
"""
from __future__ import annotations

from itertools import product
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "symbol", "timeframe", "horizon", "feature_artifact_id",
    "feature_zip_sha256", "outcome_artifact_id", "outcome_zip_sha256",
)
SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
TIMEFRAMES = ("5m", "15m", "1h")
HORIZONS = ("60", "240")
EXPECTED = set(product(SYMBOLS, TIMEFRAMES, HORIZONS))

FROZEN_SOURCE_ARTIFACTS = {
    ("EURUSD", "5m"): (
        "\"10752009633\"", "a466f0a128ea8cdc5818c6756bb71a57767f0c703eec68ad40a680f1bf9b06e2",
        "\"10759485253\"", "243824ecfb365a94dbe49442352440ffc3730240b4ca9758b0b94d8e6224534b",
    ),
    ("EURUSD", "15m"): (
        "\"10753305695\"", "a942b0bf97995cd67e94335435ab3c06ee0da7688f5ac494b79470c1c637b4ee",
        "\"10759375276\"", "dca7f656c08e7b35c51e3549cdcaf92849b2905d70cbeecc5ff1ed3773eeedd0",
    ),
    ("EURUSD", "1h"): (
        "\"10753555531\"", "831a1957519714933cc34c12fe126a88aeaf7fa9a359be6399b8569a236ee59e",
        "\"10759490258\"", "4594975177b8f7b0ff2979ddba85b774d55b65afe3da61491226dc0bb6f1eaf4",
    ),
    ("GBPUSD", "5m"): (
        "\"10753690116\"", "62bb96d9492fa092cd5aa157223be34dab6c78fb20e381a4d7804adbcec22498",
        "\"10759375400\"", "69b5a774707fe1bf26e271ad6a89084f22169a9155dc5debcbf5d00c00a2fdf4",
    ),
    ("GBPUSD", "15m"): (
        "\"10753680126\"", "c5d894f595e85f84670ac66348b0fb40366a80286408c8c1b777549a5dffdc84",
        "\"10759695313\"", "a04e9a5ffa5faaf8200385fe7a71bf1d9a56aba3021d60bae25c247b537c365f",
    ),
    ("GBPUSD", "1h"): (
        "\"10753440747\"", "f7c66064a0255585ecf5e4eca6da86bbea3eee58d38bbf9aaeecd04748a8f6f8",
        "\"10759645383\"", "b2a192ceca9031dc2460194db698318a04b99df9f346b4c32c8e9ba7803d4f49",
    ),
    ("USDJPY", "5m"): (
        "\"10752846673\"", "d719b40919b1edf1f868352c19579f30528232387df3862c7f85782d8a2a7360",
        "\"10757827671\"", "42794311c61189b95a130efafab50cc2c9586d00761e053727f7a05ecd66e36f",
    ),
    ("USDJPY", "15m"): (
        "\"10753781465\"", "5fdec186a2e086e725623682fd8143294d941635a780038070904e15ed2a4a92",
        "\"10757812657\"", "edc30a8f49b072e6504a82ae0d90d30a1a362b4dd825bf48d0ed1d2b567af2be",
    ),
    ("USDJPY", "1h"): (
        "\"10752752044\"", "bc8936d2a02bfc6cde9d11eae23330bfc047374f03fe265ed15eaa6d4d0bd3b4",
        "\"10757692733\"", "aa7fda1ca6e43c3b41a2ee1fb3729de61bb7dc6ea55e98fda70e8434770a8ee4",
    ),
}


def rows_from_checked_in_text(source: str) -> list[dict[str, str]]:
    cell = source.split("  annual_cell:\n", 1)[1].split(
        "  annual_freeze:\n", 1
    )[0]
    dataset = cell.split("        dataset:\n", 1)[1].split(
        "\n    steps:\n", 1
    )[0]
    pieces = dataset.split("          - symbol: ")
    if pieces[0].strip():
        raise ValueError("unreviewed matrix prefix or first row")
    chunks = pieces[1:]
    rows = []
    for chunk in chunks:
        lines = chunk.splitlines()
        keys = [("symbol", lines[0])]
        for line in lines[1:]:
            matched = re.fullmatch(r"            ([a-z0-9_]+): (.+)", line)
            if matched is None:
                raise ValueError("unknown matrix row source syntax")
            keys.append(matched.groups())
        if len(keys) != len(FIELDS) or len({key for key, _ in keys}) != len(FIELDS):
            raise ValueError("matrix row missing/duplicated field")
        rows.append(dict(keys))
    return rows


def matrix_source_review(source: object) -> tuple[str, ...]:
    if type(source) is not str:
        return ("NON_TEXT",)
    try:
        rows = rows_from_checked_in_text(source)
    except (IndexError, ValueError):
        return ("MATRIX_SOURCE_SHAPE_UNREVIEWED",)
    issues = []
    if len(rows) != 18:
        issues.append("MATRIX_CELL_COUNT_DRIFT")
    if any(set(row) != set(FIELDS) for row in rows):
        # Unknown/missing keys must never reach direct dict-index lookups.
        return ("MATRIX_FIELDS_DRIFT",)
    keys = [(row.get("symbol"), row.get("timeframe"), row.get("horizon"))
            for row in rows]
    if set(keys) != EXPECTED or len(set(keys)) != len(keys):
        issues.append("MATRIX_COMBINATIONS_DRIFT")
    previous: dict[tuple[str, str], tuple[str, ...]] = {}
    feature_sources: dict[tuple[str, str], tuple[str, str]] = {}
    outcome_sources: dict[tuple[str, str], tuple[str, str]] = {}
    for row in rows:
        ids = (row["feature_artifact_id"], row["outcome_artifact_id"])
        digests = (row["feature_zip_sha256"], row["outcome_zip_sha256"])
        if any(re.fullmatch(r'"[1-9][0-9]*"', value) is None for value in ids):
            issues.append("MATRIX_ARTIFACT_ID_UNREVIEWED")
        if any(re.fullmatch(r"[0-9a-f]{64}", value) is None for value in digests):
            issues.append("MATRIX_DIGEST_FORMAT_UNREVIEWED")
        pair = (row["symbol"], row["timeframe"])
        identity = (ids[0], digests[0], ids[1], digests[1])
        if pair in previous and previous[pair] != identity:
            issues.append("MATRIX_PAIR_SOURCE_CONFLICT")
        previous[pair] = identity
        for collection, identity_part in (
            (feature_sources, (ids[0], digests[0])),
            (outcome_sources, (ids[1], digests[1])),
        ):
            if pair in collection and collection[pair] != identity_part:
                issues.append("MATRIX_PAIR_SOURCE_CONFLICT")
            collection[pair] = identity_part
    if (len(set(feature_sources.values())) != 9 or
            len(set(outcome_sources.values())) != 9):
        issues.append("MATRIX_DISTINCT_SOURCE_PAIRS_DRIFT")
    return tuple(sorted(set(issues)))


def pinned_archive_source_review(source: object) -> tuple[str, ...]:
    """Check exact reviewed workflow literals, not remote artifact bytes."""
    if type(source) is not str:
        return ("NON_TEXT",)
    if matrix_source_review(source):
        return ("MATRIX_BASE_SOURCE_UNREVIEWED",)
    try:
        rows = rows_from_checked_in_text(source)
    except (IndexError, ValueError, KeyError):
        return ("MATRIX_BASE_SOURCE_UNREVIEWED",)
    issues = []
    for row in rows:
        pair = (row["symbol"], row["timeframe"])
        current = (
            row["feature_artifact_id"], row["feature_zip_sha256"],
            row["outcome_artifact_id"], row["outcome_zip_sha256"],
        )
        if FROZEN_SOURCE_ARTIFACTS.get(pair) != current:
            issues.append("REVIEWED_ARTIFACT_LITERAL_IDENTITY_DRIFT")
    if {r["symbol"] for r in rows} != set(SYMBOLS):
        issues.append("SYMBOL_SET_DRIFT")
    return tuple(sorted(set(issues)))


def matrix_strategy_source_review(source: object) -> tuple[str, ...]:
    """Narrow syntactic guard against unreviewed matrix axes/include/exclude."""
    if type(source) is not str:
        return ("NON_TEXT",)
    try:
        cell = source.split("  annual_cell:\n", 1)[1].split(
            "  annual_freeze:\n", 1)[0]
        if cell.count("    strategy:\n") != 1:
            return ("MATRIX_STRATEGY_SHAPE_UNREVIEWED",)
        if cell.count("      matrix:\n") != 1:
            return ("MATRIX_CONTAINER_SHAPE_UNREVIEWED",)
        if cell.count("        dataset:\n") != 1:
            return ("MATRIX_DATASET_SHAPE_UNREVIEWED",)
        if cell.count("    steps:\n") != 1:
            return ("MATRIX_STEPS_BOUNDARY_UNREVIEWED",)
        before_matrix = cell.split("    strategy:\n", 1)[1].split(
            "      matrix:\n", 1)[0]
        before_dataset = cell.split("      matrix:\n", 1)[1].split(
            "        dataset:\n", 1)[0]
        if before_matrix != ("      fail-fast: false\n"
                             "      max-parallel: 3\n"):
            return ("MATRIX_STRATEGY_KEYS_UNREVIEWED",)
        if before_dataset:
            return ("MATRIX_ADDITIONAL_AXIS_UNREVIEWED",)
        if matrix_source_review(source):
            return ("MATRIX_ROW_SOURCE_UNREVIEWED",)
    except (IndexError, ValueError):
        return ("MATRIX_SOURCE_SHAPE_UNREVIEWED",)
    return ()


class AnnualMatrixSourceIsNotImmutableArtifactProvenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = subprocess.check_output(
            ["git", "show",
             "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True,
        )

    def test_checked_in_matrix_matches_18_cell_source_inventory(self):
        self.assertEqual(matrix_source_review(self.source), ())

    def test_expected_cross_product_exactly_once(self):
        rows = rows_from_checked_in_text(self.source)
        self.assertEqual({(r["symbol"], r["timeframe"], r["horizon"])
                          for r in rows}, EXPECTED)
        self.assertEqual(len(rows), len(EXPECTED))

    def test_exactly_nine_feature_and_outcome_pairs(self):
        rows = rows_from_checked_in_text(self.source)
        self.assertEqual(len({(r["feature_artifact_id"],
                               r["feature_zip_sha256"]) for r in rows}), 9)
        self.assertEqual(len({(r["outcome_artifact_id"],
                               r["outcome_zip_sha256"]) for r in rows}), 9)

    def test_duplicate_cell_combo_is_detected(self):
        altered = self.source.replace(
            "          - symbol: EURUSD\n            timeframe: 5m\n"
            "            horizon: 60\n",
            "          - symbol: EURUSD\n            timeframe: 5m\n"
            "            horizon: 240\n", 1)
        self.assertIn("MATRIX_COMBINATIONS_DRIFT", matrix_source_review(altered))

    def test_missing_symbol_requires_review(self):
        altered = self.source.replace(
            "          - symbol: EURUSD\n", "          - symbol: AUDUSD\n", 1)
        self.assertIn("MATRIX_COMBINATIONS_DRIFT", matrix_source_review(altered))

    def test_unreviewed_timeframe_requires_review(self):
        altered = self.source.replace(
            "            timeframe: 5m\n", "            timeframe: 30m\n", 1)
        self.assertIn("MATRIX_COMBINATIONS_DRIFT", matrix_source_review(altered))

    def test_unreviewed_horizon_requires_review(self):
        altered = self.source.replace(
            "            horizon: 60\n", "            horizon: 90\n", 1)
        self.assertIn("MATRIX_COMBINATIONS_DRIFT", matrix_source_review(altered))

    def test_changed_artifact_id_between_horizons_fails(self):
        altered = self.source.replace(
            'feature_artifact_id: "10752009633"',
            'feature_artifact_id: "10752009634"', 1)
        self.assertIn("MATRIX_PAIR_SOURCE_CONFLICT", matrix_source_review(altered))

    def test_changed_sha_between_horizons_fails(self):
        altered = self.source.replace(
            "feature_zip_sha256: a466f0a128ea8cdc5818c6756bb71a57767f0c703eec68ad40a680f1bf9b06e2",
            "feature_zip_sha256: b466f0a128ea8cdc5818c6756bb71a57767f0c703eec68ad40a680f1bf9b06e2",
            1)
        self.assertIn("MATRIX_PAIR_SOURCE_CONFLICT", matrix_source_review(altered))

    def test_nonhex_digest_is_rejected(self):
        altered = self.source.replace(
            "feature_zip_sha256: a466f0a128ea8cdc5818c6756bb71a57767f0c703eec68ad40a680f1bf9b06e2",
            "feature_zip_sha256: z466f0a128ea8cdc5818c6756bb71a57767f0c703eec68ad40a680f1bf9b06e2",
            1)
        self.assertIn("MATRIX_DIGEST_FORMAT_UNREVIEWED",
                      matrix_source_review(altered))

    def test_nonnumeric_artifact_id_is_rejected(self):
        altered = self.source.replace(
            'feature_artifact_id: "10752009633"',
            'feature_artifact_id: "not-an-id"', 1)
        self.assertIn("MATRIX_ARTIFACT_ID_UNREVIEWED",
                      matrix_source_review(altered))

    def test_duplicate_yaml_row_scalar_requires_review(self):
        altered = self.source.replace(
            "            horizon: 60\n",
            "            horizon: 60\n            horizon: 60\n", 1)
        self.assertIn("MATRIX_SOURCE_SHAPE_UNREVIEWED",
                      matrix_source_review(altered))

    def test_unknown_matrix_scalar_requires_review(self):
        altered = self.source.replace(
            "            horizon: 60\n",
            "            horizon: 60\n            extra: unreviewed\n", 1)
        self.assertIn("MATRIX_SOURCE_SHAPE_UNREVIEWED",
                      matrix_source_review(altered))

    def test_nontext_source_is_not_a_valid_review_input(self):
        self.assertEqual(matrix_source_review(None), ("NON_TEXT",))

    def test_sha256_field_names_parse_in_all_eighteen_rows(self):
        rows = rows_from_checked_in_text(self.source)
        self.assertEqual(len(rows), 18)
        for row in rows:
            with self.subTest(pair=(row["symbol"], row["timeframe"],
                                    row["horizon"])):
                self.assertIn("feature_zip_sha256", row)
                self.assertIn("outcome_zip_sha256", row)
                self.assertEqual(len(row["feature_zip_sha256"]), 64)
                self.assertEqual(len(row["outcome_zip_sha256"]), 64)

    def test_each_real_matrix_row_has_seven_source_fields(self):
        for row in rows_from_checked_in_text(self.source):
            self.assertEqual(set(row), set(FIELDS))

    def test_unexpected_numeric_label_is_not_silently_ignored(self):
        changed = self.source.replace(
            "            horizon: 60\n",
            "            horizon: 60\n            unreviewed2: 1\n", 1)
        self.assertEqual(matrix_source_review(changed),
                         ("MATRIX_SOURCE_SHAPE_UNREVIEWED",))

    def test_duplicate_sha256_key_is_not_silently_ignored(self):
        field = ("            feature_zip_sha256: "
                 "a466f0a128ea8cdc5818c6756bb71a57767f0c703eec68ad40a680f1bf9b06e2\n")
        changed = self.source.replace(field, field + field, 1)
        self.assertEqual(matrix_source_review(changed),
                         ("MATRIX_SOURCE_SHAPE_UNREVIEWED",))

    def test_malformed_digest_key_requires_explicit_review(self):
        changed = self.source.replace(
            "            feature_zip_sha256: ",
            "            feature_zip_sha-256: ", 1)
        self.assertEqual(matrix_source_review(changed),
                         ("MATRIX_SOURCE_SHAPE_UNREVIEWED",))

    def test_reviewed_18_cell_literal_ids_and_hashes_are_pinned(self):
        self.assertEqual(pinned_archive_source_review(self.source), ())

    def test_reviewed_snapshot_has_nine_expected_symbol_timeframe_pairs(self):
        self.assertEqual(set(FROZEN_SOURCE_ARTIFACTS),
                         set(product(SYMBOLS, TIMEFRAMES)))

    def test_both_horizons_changed_feature_id_is_not_silently_accepted(self):
        changed = self.source.replace(
            'feature_artifact_id: "10752009633"',
            'feature_artifact_id: "10752009634"')
        self.assertEqual(matrix_source_review(changed), ())
        self.assertIn("REVIEWED_ARTIFACT_LITERAL_IDENTITY_DRIFT",
                      pinned_archive_source_review(changed))

    def test_both_horizons_changed_outcome_id_requires_review(self):
        changed = self.source.replace(
            'outcome_artifact_id: "10759485253"',
            'outcome_artifact_id: "10759485254"')
        self.assertEqual(matrix_source_review(changed), ())
        self.assertIn("REVIEWED_ARTIFACT_LITERAL_IDENTITY_DRIFT",
                      pinned_archive_source_review(changed))

    def test_both_horizons_changed_feature_sha_requires_review(self):
        original = "a466f0a128ea8cdc5818c6756bb71a57767f0c703eec68ad40a680f1bf9b06e2"
        changed = self.source.replace(original, "b" + original[1:])
        self.assertEqual(matrix_source_review(changed), ())
        self.assertIn("REVIEWED_ARTIFACT_LITERAL_IDENTITY_DRIFT",
                      pinned_archive_source_review(changed))

    def test_both_horizons_changed_outcome_sha_requires_review(self):
        original = "243824ecfb365a94dbe49442352440ffc3730240b4ca9758b0b94d8e6224534b"
        changed = self.source.replace(original, "a" + original[1:])
        self.assertEqual(matrix_source_review(changed), ())
        self.assertIn("REVIEWED_ARTIFACT_LITERAL_IDENTITY_DRIFT",
                      pinned_archive_source_review(changed))

    def test_valid_shape_does_not_replace_literal_artifact_identity(self):
        original = 'feature_artifact_id: "10753305695"'
        changed = self.source.replace(original,
                                      'feature_artifact_id: "10753305696"')
        self.assertEqual(matrix_source_review(changed), ())
        self.assertNotEqual(pinned_archive_source_review(changed), ())

    def test_single_horizon_mutation_stays_a_base_source_failure(self):
        changed = self.source.replace(
            'feature_artifact_id: "10752009633"',
            'feature_artifact_id: "10752009634"', 1)
        self.assertIn("MATRIX_BASE_SOURCE_UNREVIEWED",
                      pinned_archive_source_review(changed))

    def test_untrusted_nontext_source_stays_blocked(self):
        self.assertEqual(pinned_archive_source_review([]), ("NON_TEXT",))

    def test_current_matrix_outer_grammar_has_no_drift(self):
        self.assertEqual(matrix_strategy_source_review(self.source), ())

    def test_include_before_dataset_is_flagged(self):
        changed = self.source.replace(
            "        dataset:\n",
            "        include:\n          - extra: unexpected\n"
            "        dataset:\n", 1)
        self.assertEqual(matrix_strategy_source_review(changed),
                         ("MATRIX_ADDITIONAL_AXIS_UNREVIEWED",))

    def test_exclude_before_dataset_is_flagged(self):
        changed = self.source.replace(
            "        dataset:\n",
            "        exclude:\n          - symbol: EURUSD\n"
            "        dataset:\n", 1)
        self.assertEqual(matrix_strategy_source_review(changed),
                         ("MATRIX_ADDITIONAL_AXIS_UNREVIEWED",))

    def test_new_matrix_axis_before_dataset_is_flagged(self):
        changed = self.source.replace(
            "        dataset:\n",
            "        extra_axis: [on, off]\n        dataset:\n", 1)
        self.assertEqual(matrix_strategy_source_review(changed),
                         ("MATRIX_ADDITIONAL_AXIS_UNREVIEWED",))

    def test_duplicate_matrix_key_does_not_pass_as_reviewed(self):
        changed = self.source.replace(
            "      matrix:\n", "      matrix:\n      matrix:\n", 1)
        self.assertEqual(matrix_strategy_source_review(changed),
                         ("MATRIX_CONTAINER_SHAPE_UNREVIEWED",))

    def test_unexpected_strategy_scalar_does_not_pass(self):
        changed = self.source.replace(
            "      max-parallel: 3\n",
            "      max-parallel: 3\n      experimental: enabled\n", 1)
        self.assertEqual(matrix_strategy_source_review(changed),
                         ("MATRIX_STRATEGY_KEYS_UNREVIEWED",))

    def test_missing_strategy_header_does_not_pass(self):
        changed = self.source.replace(
            "    strategy:\n", "    different_strategy:\n", 1)
        self.assertEqual(matrix_strategy_source_review(changed),
                         ("MATRIX_STRATEGY_SHAPE_UNREVIEWED",))

    def test_alternate_matrix_container_requires_review(self):
        changed = self.source.replace(
            "      matrix:\n", "      matrix: unreviewed-expression\n", 1)
        self.assertEqual(matrix_strategy_source_review(changed),
                         ("MATRIX_CONTAINER_SHAPE_UNREVIEWED",))

    def test_missing_cell_steps_boundary_requires_review(self):
        cell = self.source.split("  annual_cell:\n", 1)[1].split(
            "  annual_freeze:\n", 1)[0]
        changed_cell = cell.replace(
            "    steps:\n", "    changed_steps:\n", 1)
        changed = self.source.replace(cell, changed_cell, 1)
        self.assertEqual(matrix_strategy_source_review(changed),
                         ("MATRIX_STEPS_BOUNDARY_UNREVIEWED",))

    def test_nontext_outer_matrix_review_rejected(self):
        self.assertEqual(matrix_strategy_source_review({}), ("NON_TEXT",))

    def test_unknown_feature_id_field_is_reported_not_raised(self):
        changed = self.source.replace(
            "            feature_artifact_id: ",
            "            unreviewed_feature_id: ", 1)
        self.assertEqual(matrix_source_review(changed),
                         ("MATRIX_FIELDS_DRIFT",))

    def test_unknown_outcome_digest_field_is_reported_not_raised(self):
        changed = self.source.replace(
            "            outcome_zip_sha256: ",
            "            unreviewed_outcome_sha256: ", 1)
        self.assertEqual(matrix_source_review(changed),
                         ("MATRIX_FIELDS_DRIFT",))

    def test_unknown_first_row_key_is_reported_not_ignored(self):
        changed = self.source.replace(
            "          - symbol: EURUSD\n",
            "          - unreviewed_symbol: EURUSD\n", 1)
        self.assertEqual(matrix_source_review(changed),
                         ("MATRIX_SOURCE_SHAPE_UNREVIEWED",))

    def test_unknown_timeframe_key_is_reported_not_raised(self):
        changed = self.source.replace(
            "            timeframe: 5m\n",
            "            unreviewed_frame: 5m\n", 1)
        self.assertEqual(matrix_source_review(changed),
                         ("MATRIX_FIELDS_DRIFT",))

    def test_noncanonical_field_name_blocks_literal_pin_review(self):
        changed = self.source.replace(
            "            feature_zip_sha256: ",
            "            unreviewed_digest_name: ", 1)
        self.assertEqual(pinned_archive_source_review(changed),
                         ("MATRIX_BASE_SOURCE_UNREVIEWED",))

    def test_noncanonical_field_name_blocks_strategy_review(self):
        changed = self.source.replace(
            "            outcome_artifact_id: ",
            "            alternate_outcome_id: ", 1)
        self.assertEqual(matrix_strategy_source_review(changed),
                         ("MATRIX_ROW_SOURCE_UNREVIEWED",))

    def test_canonical_pinned_matrix_remains_accepted(self):
        self.assertEqual(matrix_source_review(self.source), ())
        self.assertEqual(pinned_archive_source_review(self.source), ())
        self.assertEqual(matrix_strategy_source_review(self.source), ())

    def test_first_row_prefix_comment_requires_shape_review(self):
        changed = self.source.replace(
            "        dataset:\n",
            "        dataset:\n          # unreviewed prefix\n", 1)
        self.assertEqual(matrix_source_review(changed),
                         ("MATRIX_SOURCE_SHAPE_UNREVIEWED",))

    def test_first_symbol_row_must_not_silently_disappear(self):
        changed = self.source.replace(
            "          - symbol: EURUSD\n",
            "          - renamed_symbol: EURUSD\n", 1)
        self.assertEqual(matrix_source_review(changed),
                         ("MATRIX_SOURCE_SHAPE_UNREVIEWED",))

    def test_first_unknown_row_does_not_satisfy_reviewed_literal_pins(self):
        changed = self.source.replace(
            "          - symbol: EURUSD\n",
            "          - alternative_row: EURUSD\n", 1)
        self.assertEqual(pinned_archive_source_review(changed),
                         ("MATRIX_BASE_SOURCE_UNREVIEWED",))

    def test_canonical_source_still_has_eighteen_parsed_rows(self):
        self.assertEqual(len(rows_from_checked_in_text(self.source)), 18)
        self.assertEqual(matrix_source_review(self.source), ())
