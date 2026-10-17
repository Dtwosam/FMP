"""DEC-1462: offline exact Phase3 log index and upload receipt parser.

No real artifact access, GitHub API, protected annual execution, brokerage
or security setting mutation. Caller must independently authenticate log text.
"""
from __future__ import annotations

from datetime import datetime
import json
import re
import unittest

PREFIX = r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z) "
INDEX = re.compile(PREFIX + r'(\{"code_commit":.*\})$')
NAME = re.compile(PREFIX + r"  name: (phase3-backtester-acceptance-[0-9a-f]{40})$")
FINAL = re.compile(PREFIX + r"Artifact (phase3-backtester-acceptance-[0-9a-f]{40})"
                   r"\.zip successfully finalized\. Artifact ID ([1-9][0-9]*)$")
UPLOAD = re.compile(PREFIX + r"Artifact (phase3-backtester-acceptance-[0-9a-f]{40}) "
                    r"has been successfully uploaded! Final size is ([1-9][0-9]*) "
                    r"bytes\. Artifact ID is ([1-9][0-9]*)$")
URL = re.compile(PREFIX + r"Artifact download URL: "
                 r"https://github.com/Dtwosam/FMP/actions/runs/([1-9][0-9]*)"
                 r"/artifacts/([1-9][0-9]*)$")
SHA = re.compile(r"[0-9a-f]{64}\Z")
SCENARIOS = ("ambiguity", "daily-halt-reset", "long-cost",
             "short-target", "simultaneous-risk")


def _unique_json_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def parse_phase3_log_evidence(raw_log, run_id, expected_merge_sha):
    """Return (index, upload, issues), using four immutable-looking log stages.

    Source consistency is not independently authenticated GitHub provenance.
    """
    if (type(raw_log) is not str or type(run_id) is not int or run_id <= 0 or
            type(expected_merge_sha) is not str or
            re.fullmatch(r"[0-9a-f]{40}", expected_merge_sha) is None):
        return None, None, ("PHASE3_RAW_LOG_INPUT_UNREVIEWED",)
    patterns = {"index": INDEX, "name": NAME, "final": FINAL,
                "upload": UPLOAD, "url": URL}
    found = {
        name: [(i, match.groups())
               for i, line in enumerate(raw_log.splitlines())
               if (match := pattern.fullmatch(line)) is not None]
        for name, pattern in patterns.items()
    }
    if any(len(records) != 1 for records in found.values()):
        return None, None, ("PHASE3_RAW_LOG_STAGE_CARDINALITY_UNREVIEWED",)
    stage = [found[name][0] for name in patterns]
    issues = []
    if [i for i, _ in stage] != sorted(i for i, _ in stage):
        issues.append("PHASE3_RAW_LOG_STAGE_ORDER_UNREVIEWED")
    try:
        times = [datetime.fromisoformat(entry[0].replace("Z", "+00:00"))
                 for _, entry in stage]
    except (ValueError, TypeError, OverflowError):
        issues.append("PHASE3_RAW_LOG_TIMESTAMP_UNREVIEWED")
    else:
        if not all(a < b for a, b in zip(times, times[1:])):
            issues.append("PHASE3_RAW_LOG_TIMESTAMP_ORDER_UNREVIEWED")
    try:
        index = json.loads(found["index"][0][1][1],
                           object_pairs_hook=_unique_json_pairs)
    except (json.JSONDecodeError, ValueError, TypeError):
        return None, None, tuple(sorted(set(
            issues + ["PHASE3_RAW_INDEX_JSON_UNREVIEWED"])))
    if type(index) is not dict:
        issues.append("PHASE3_RAW_INDEX_SHAPE_UNREVIEWED")
        return None, None, tuple(sorted(set(issues)))
    if (index.get("code_commit") != expected_merge_sha or
            index.get("protocol") != "fmp-phase3-acceptance-fixture-v1" or
            index.get("fixture_id") != "phase3-merged-main-acceptance-v1" or
            type(index.get("scenario_count")) is not int or
            index["scenario_count"] != 5):
        issues.append("PHASE3_RAW_INDEX_IDENTITY_UNREVIEWED")
    scenarios = index.get("scenarios")
    if type(scenarios) is not list or len(scenarios) != 5 or not all(
            type(v) is dict for v in scenarios):
        issues.append("PHASE3_RAW_SCENARIO_INVENTORY_UNREVIEWED")
    else:
        if tuple(s.get("name") for s in scenarios) != SCENARIOS:
            issues.append("PHASE3_RAW_SCENARIO_NAMES_UNREVIEWED")
        for scenario in scenarios:
            primary = scenario.get("primary_manifest_sha256")
            repeat = scenario.get("repeat_manifest_sha256")
            if (scenario.get("bytes_equal") is not True or
                    type(primary) is not str or SHA.fullmatch(primary) is None or
                    repeat != primary or
                    any(type(scenario.get(k)) is not int or scenario[k] < 0
                        for k in ("trade_count", "rejection_count"))):
                issues.append("PHASE3_RAW_SCENARIO_DETERMINISM_UNREVIEWED")
    name = found["name"][0][1][1]
    finalized_name, finalized_id = found["final"][0][1][1:]
    uploaded_name, size, uploaded_id = found["upload"][0][1][1:]
    url_run, url_id = found["url"][0][1][1:]
    expected_name = "phase3-backtester-acceptance-" + expected_merge_sha
    if any(value != expected_name for value in (
            name, finalized_name, uploaded_name)):
        issues.append("PHASE3_RAW_UPLOAD_MERGE_NAME_MISMATCH")
    if not (finalized_id == uploaded_id == url_id and int(url_run) == run_id):
        issues.append("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH")
    receipt = {
        "name": name, "id": int(finalized_id), "run_id": int(url_run),
        "finalized": True, "size_bytes": int(size),
    }
    return index, receipt, tuple(sorted(set(issues)))


class Phase3LogEvidenceIsNotProtectedResearchPermission(unittest.TestCase):
    def setUp(self):
        self.merge = "7630c183c7aca3e72a01b405b342c73db228c845"
        self.run_id = 39026055591
        self.artifact_id = 12098433056
        self.name = "phase3-backtester-acceptance-" + self.merge
        self.index = {
            "code_commit": self.merge,
            "fixture_id": "phase3-merged-main-acceptance-v1",
            "protocol": "fmp-phase3-acceptance-fixture-v1",
            "scenario_count": 5,
            "scenarios": [
                {"name": name, "bytes_equal": True, "primary_manifest_sha256": "a"*64,
                 "repeat_manifest_sha256": "a"*64, "trade_count": 1,
                 "rejection_count": 0} for name in SCENARIOS
            ],
        }
        self.lines = [
            "2026-10-17T10:44:58.9660091Z " +
                json.dumps(self.index, separators=(",", ":")),
            "2026-10-17T10:44:59.0284559Z   name: " + self.name,
            "2026-10-17T10:45:00.0166354Z Artifact " + self.name +
                ".zip successfully finalized. Artifact ID " + str(self.artifact_id),
            "2026-10-17T10:45:00.0169230Z Artifact " + self.name +
                " has been successfully uploaded! Final size is 23504 bytes. "
                "Artifact ID is " + str(self.artifact_id),
            "2026-10-17T10:45:00.0171215Z Artifact download URL: "
                "https://github.com/Dtwosam/FMP/actions/runs/" +
                str(self.run_id) + "/artifacts/" + str(self.artifact_id),
        ]

    def verdict(self):
        return parse_phase3_log_evidence(
            "\n".join(self.lines), self.run_id, self.merge)

    def test_index_and_upload_receipt_parse_without_artifact_download(self):
        idx, receipt, errors = self.verdict()
        self.assertEqual(errors, ())
        self.assertEqual(idx["code_commit"], self.merge)
        self.assertEqual(receipt["run_id"], self.run_id)
        self.assertEqual(receipt["id"], self.artifact_id)

    def test_wrong_index_merge_sha_is_rejected(self):
        self.lines[0] = self.lines[0].replace(self.merge, "b"*40)
        self.assertIn("PHASE3_RAW_INDEX_IDENTITY_UNREVIEWED", self.verdict()[2])

    def test_wrong_artifact_name_sha_is_rejected(self):
        self.lines[1] = self.lines[1].replace(self.merge, "b"*40)
        self.assertIn("PHASE3_RAW_UPLOAD_MERGE_NAME_MISMATCH",
                      self.verdict()[2])

    def test_finalized_artifact_id_mismatch_is_rejected(self):
        self.lines[2] = self.lines[2].replace(str(self.artifact_id), "101")
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH", self.verdict()[2])

    def test_download_url_other_run_is_rejected_without_fetching(self):
        self.lines[4] = self.lines[4].replace(str(self.run_id), "101")
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH", self.verdict()[2])

    def test_index_malformed_json_fails(self):
        self.lines[0] = self.lines[0].replace('"scenario_count":5',
                                              '"scenario_count":')
        self.assertIn("PHASE3_RAW_INDEX_JSON_UNREVIEWED", self.verdict()[2])

    def test_duplicate_top_level_json_key_fails(self):
        self.lines[0] = self.lines[0].replace('{"code_commit":',
                                              '{"code_commit":"' + self.merge +
                                              '","code_commit":')
        self.assertIn("PHASE3_RAW_INDEX_JSON_UNREVIEWED", self.verdict()[2])

    def test_missing_index_line_fails(self):
        self.lines.pop(0)
        self.assertIn("PHASE3_RAW_LOG_STAGE_CARDINALITY_UNREVIEWED",
                      self.verdict()[2])

    def test_duplicate_uploaded_line_fails(self):
        self.lines.append(self.lines[3])
        self.assertIn("PHASE3_RAW_LOG_STAGE_CARDINALITY_UNREVIEWED",
                      self.verdict()[2])

    def test_wrong_stage_order_fails(self):
        self.lines[1], self.lines[2] = self.lines[2], self.lines[1]
        self.assertIn("PHASE3_RAW_LOG_STAGE_ORDER_UNREVIEWED",
                      self.verdict()[2])

    def test_impossible_timestamp_fails(self):
        self.lines[1] = self.lines[1].replace("2026-10-17", "2026-99-17")
        self.assertIn("PHASE3_RAW_LOG_TIMESTAMP_UNREVIEWED",
                      self.verdict()[2])

    def test_missing_scenario_fails(self):
        self.index["scenarios"].pop()
        self.lines[0] = self.lines[0].split("Z ",1)[0] + "Z " + json.dumps(
            self.index, separators=(",", ":"))
        self.assertIn("PHASE3_RAW_SCENARIO_INVENTORY_UNREVIEWED",
                      self.verdict()[2])

    def test_inconsistent_manifest_sha_is_rejected(self):
        self.index["scenarios"][0]["repeat_manifest_sha256"] = "b"*64
        self.lines[0] = self.lines[0].split("Z ",1)[0] + "Z " + json.dumps(
            self.index, separators=(",", ":"))
        self.assertIn("PHASE3_RAW_SCENARIO_DETERMINISM_UNREVIEWED",
                      self.verdict()[2])

    def test_non_utf8_log_or_wrong_run_type_is_rejected(self):
        self.assertEqual(parse_phase3_log_evidence(None, self.run_id, self.merge)[2],
                         ("PHASE3_RAW_LOG_INPUT_UNREVIEWED",))
        self.assertEqual(parse_phase3_log_evidence("\n".join(self.lines), True,
                                                  self.merge)[2],
                         ("PHASE3_RAW_LOG_INPUT_UNREVIEWED",))

    def test_log_record_consistency_is_not_os_or_dispatch_admission(self):
        self.assertEqual(self.verdict()[2], ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict()[2])
