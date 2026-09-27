from __future__ import annotations

import hashlib
import json
from typing import Mapping, Sequence

from fmp.market_learning.evidence import EXPECTED_SOURCE_MANIFEST_SHA256

from .market_learning_adapter import validate_cell_evidence
from .pattern_protocol import (
    DISCOVERY_CELLS,
    EXPERIMENT_ID,
    MAX_DISCOVERY_SHORTLIST,
    MAX_FROZEN_PATTERN_HYPOTHESES,
    protocol_fingerprint,
)


EXP061_RUN_CONTRACT_DECISION = "DEC-274"
EXP061_RUN_CONTRACT_VERSION = "fmp-exp061-run-contract-v1"
EXP061_AGGREGATE_EVIDENCE_VERSION = 1
EXP061_AGGREGATE_EVIDENCE_PROTOCOL = "fmp-exp061-aggregate-evidence-v1"

WORKFLOW_NAME = "phase8a-exp061-discovery"
WORKFLOW_PATH = ".github/workflows/phase8a-exp061-discovery.yml"
WORKFLOW_EVENT = "workflow_dispatch"
WORKFLOW_BRANCH = "main"
WORKFLOW_RUN_ATTEMPT = 1

PREFLIGHT_JOB_NAME = "exp061-preflight"
AGGREGATE_JOB_NAME = "exp061-aggregate"

PROTOCOL_SOURCE_BLOB_SHA = "63b3f0121d6a50eb9e8e62ab666d70eb91791621"
MINER_SOURCE_BLOB_SHA = "495a67699eb5014e52129f0238a2737049fe38e6"
ADAPTER_SOURCE_BLOB_SHA = "978a33554fad7e9d78b002778c4896be0af3333a"
LOADER_SOURCE_BLOB_SHA = "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea"

WORKFLOW_SOURCE_AUTHORIZED = False
WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False

EXPECTED_CELLS = tuple(DISCOVERY_CELLS)
EXPECTED_CELL_COUNT = 18
EXPECTED_JOB_COUNT = 20
EXPECTED_ARTIFACT_COUNT = 20


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def _validate_commit(value: object, *, field: str = "code_commit") -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def expected_cell_job_name(
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> str:
    cell = (symbol, timeframe, horizon_minutes)
    if cell not in EXPECTED_CELLS:
        raise ValueError("unsupported EXP-061 run-contract cell")
    return f"exp061-cell-{symbol}-{timeframe}-{horizon_minutes}m"


def expected_cell_artifact_name(
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
    *,
    code_commit: str,
) -> str:
    _validate_commit(code_commit)
    return (
        f"phase8a-exp061-cell-{symbol}-{timeframe}-"
        f"{horizon_minutes}m-{code_commit}"
    )


def expected_preflight_artifact_name(*, code_commit: str) -> str:
    _validate_commit(code_commit)
    return f"phase8a-exp061-preflight-{code_commit}"


def expected_aggregate_artifact_name(*, code_commit: str) -> str:
    _validate_commit(code_commit)
    return f"phase8a-exp061-aggregate-{code_commit}"


def expected_job_names() -> tuple[str, ...]:
    return (
        PREFLIGHT_JOB_NAME,
        *(
            expected_cell_job_name(symbol, timeframe, horizon)
            for symbol, timeframe, horizon in EXPECTED_CELLS
        ),
        AGGREGATE_JOB_NAME,
    )


def expected_artifact_names(*, code_commit: str) -> tuple[str, ...]:
    _validate_commit(code_commit)
    return (
        expected_preflight_artifact_name(code_commit=code_commit),
        *(
            expected_cell_artifact_name(
                symbol,
                timeframe,
                horizon,
                code_commit=code_commit,
            )
            for symbol, timeframe, horizon in EXPECTED_CELLS
        ),
        expected_aggregate_artifact_name(code_commit=code_commit),
    )


def run_contract_payload(*, code_commit: str) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    jobs = expected_job_names()
    artifacts = expected_artifact_names(code_commit=code_commit)
    if len(jobs) != EXPECTED_JOB_COUNT or len(set(jobs)) != EXPECTED_JOB_COUNT:
        raise ValueError("EXP-061 run-contract job inventory drift")
    if (
        len(artifacts) != EXPECTED_ARTIFACT_COUNT
        or len(set(artifacts)) != EXPECTED_ARTIFACT_COUNT
    ):
        raise ValueError("EXP-061 run-contract artifact inventory drift")

    return {
        "decision": EXP061_RUN_CONTRACT_DECISION,
        "contract_version": EXP061_RUN_CONTRACT_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "code_commit": code_commit,
        "workflow": {
            "name": WORKFLOW_NAME,
            "path": WORKFLOW_PATH,
            "event": WORKFLOW_EVENT,
            "branch": WORKFLOW_BRANCH,
            "run_attempt": WORKFLOW_RUN_ATTEMPT,
        },
        "upstream_source_blobs": {
            "pattern_protocol": PROTOCOL_SOURCE_BLOB_SHA,
            "pattern_miner": MINER_SOURCE_BLOB_SHA,
            "market_learning_adapter": ADAPTER_SOURCE_BLOB_SHA,
            "range_limited_loader": LOADER_SOURCE_BLOB_SHA,
        },
        "cells": [
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "horizon_minutes": horizon,
                "job_name": expected_cell_job_name(symbol, timeframe, horizon),
                "artifact_name": expected_cell_artifact_name(
                    symbol,
                    timeframe,
                    horizon,
                    code_commit=code_commit,
                ),
            }
            for symbol, timeframe, horizon in EXPECTED_CELLS
        ],
        "expected_job_names": list(jobs),
        "expected_artifact_names": list(artifacts),
        "success_shape": {
            "job_count": EXPECTED_JOB_COUNT,
            "artifact_count": EXPECTED_ARTIFACT_COUNT,
            "all_jobs_success": True,
            "all_artifacts_non_expired": True,
            "aggregate_evidence_required": True,
            "result_review_required": True,
        },
        "non_success_shape": {
            "slot_consumed_if_later_authorized": True,
            "rerun_authorized": RERUN_AUTHORIZED,
            "retry_authorized": RETRY_AUTHORIZED,
            "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
            "partial_expected_cell_evidence_may_be_preserved": True,
            "aggregate_success_evidence_required": False,
        },
        "authorizations": {
            "workflow_source_authorized": WORKFLOW_SOURCE_AUTHORIZED,
            "workflow_dispatch_authorized": WORKFLOW_DISPATCH_AUTHORIZED,
            "historical_discovery_execution_authorized": (
                HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
            ),
            "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
            "rerun_authorized": RERUN_AUTHORIZED,
            "retry_authorized": RETRY_AUTHORIZED,
            "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
            "reserved_robustness_access_authorized": (
                RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
            ),
            "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
            "promotion_authorized": PROMOTION_AUTHORIZED,
            "phase8b_authorized": PHASE8B_AUTHORIZED,
            "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
            "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
            "live_order_authorized": LIVE_ORDER_AUTHORIZED,
            "real_money_authorized": REAL_MONEY_AUTHORIZED,
            "trading_authorized": TRADING_AUTHORIZED,
        },
    }


def _cell_identity(value: Mapping[str, object]) -> tuple[str, str, int]:
    raw = value.get("cell")
    if not isinstance(raw, Mapping):
        raise ValueError("EXP-061 aggregate cell evidence is missing cell identity")
    symbol = raw.get("symbol")
    timeframe = raw.get("timeframe")
    horizon = raw.get("horizon_minutes")
    identity = (symbol, timeframe, horizon)
    if identity not in EXPECTED_CELLS:
        raise ValueError(f"unexpected EXP-061 aggregate cell identity: {identity!r}")
    return str(symbol), str(timeframe), int(horizon)


def _fingerprint_list(
    value: Mapping[str, object],
    *,
    section: str,
    field: str,
) -> tuple[str, ...]:
    raw_section = value.get(section)
    if not isinstance(raw_section, Mapping):
        raise ValueError(f"EXP-061 aggregate {section} section is malformed")
    raw = raw_section.get(field)
    if not isinstance(raw, list):
        raise ValueError(f"EXP-061 aggregate {section}.{field} must be a list")
    out: list[str] = []
    for item in raw:
        out.append(_validate_sha256(item, field=f"{section}.{field} fingerprint"))
    if len(out) != len(set(out)):
        raise ValueError(f"EXP-061 aggregate {section}.{field} has duplicates")
    return tuple(out)


def compile_aggregate_evidence(
    cell_evidence: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    if len(cell_evidence) != EXPECTED_CELL_COUNT:
        raise ValueError(
            f"EXP-061 aggregate requires exactly {EXPECTED_CELL_COUNT} cell evidence objects"
        )

    by_cell: dict[tuple[str, str, int], Mapping[str, object]] = {}
    feature_evidence_fingerprints: set[str] = set()
    outcome_evidence_fingerprints: set[str] = set()
    source_by_symbol: dict[str, str] = {}
    manifest_pair_by_symbol_timeframe: dict[tuple[str, str], tuple[str, str]] = {}
    summaries: list[dict[str, object]] = []

    for raw in cell_evidence:
        validated = validate_cell_evidence(raw)
        if validated.get("code_commit") != code_commit:
            raise ValueError("EXP-061 aggregate cell code commit mismatch")
        cell = _cell_identity(validated)
        if cell in by_cell:
            raise ValueError(f"duplicate EXP-061 aggregate cell evidence: {cell!r}")
        by_cell[cell] = validated

        symbol, timeframe, horizon = cell
        processed_sha = _validate_sha256(
            validated.get("processed_manifest_sha256"),
            field="processed_manifest_sha256",
        )
        if processed_sha != EXPECTED_SOURCE_MANIFEST_SHA256[symbol]:
            raise ValueError("EXP-061 aggregate Phase 2 source identity mismatch")
        prior_source = source_by_symbol.setdefault(symbol, processed_sha)
        if prior_source != processed_sha:
            raise ValueError("EXP-061 aggregate symbol source identity drift")

        feature_manifest_sha = _validate_sha256(
            validated.get("feature_manifest_sha256"),
            field="feature_manifest_sha256",
        )
        outcome_manifest_sha = _validate_sha256(
            validated.get("outcome_manifest_sha256"),
            field="outcome_manifest_sha256",
        )
        pair = (feature_manifest_sha, outcome_manifest_sha)
        key = (symbol, timeframe)
        prior_pair = manifest_pair_by_symbol_timeframe.setdefault(key, pair)
        if prior_pair != pair:
            raise ValueError(
                "EXP-061 aggregate manifest identity differs across horizons"
            )

        feature_evidence_fingerprints.add(
            _validate_sha256(
                validated.get("feature_evidence_fingerprint"),
                field="feature_evidence_fingerprint",
            )
        )
        outcome_evidence_fingerprints.add(
            _validate_sha256(
                validated.get("outcome_evidence_fingerprint"),
                field="outcome_evidence_fingerprint",
            )
        )

        discovery = validated.get("discovery")
        confirmation = validated.get("confirmation")
        validation = validated.get("validation")
        if (
            not isinstance(discovery, Mapping)
            or not isinstance(confirmation, Mapping)
            or not isinstance(validation, Mapping)
        ):
            raise ValueError("EXP-061 aggregate cell result sections are malformed")

        shortlist = discovery.get("shortlist")
        frozen = confirmation.get("frozen_pattern_fingerprints")
        validated_fingerprints = validation.get("validated_pattern_fingerprints")
        if (
            not isinstance(shortlist, list)
            or not isinstance(frozen, list)
            or not isinstance(validated_fingerprints, list)
        ):
            raise ValueError("EXP-061 aggregate cell inventories are malformed")

        shortlist_fingerprints = tuple(
            _validate_sha256(
                item.get("fingerprint") if isinstance(item, Mapping) else None,
                field="discovery shortlist fingerprint",
            )
            for item in shortlist
        )
        frozen_fingerprints = _fingerprint_list(
            validated,
            section="confirmation",
            field="frozen_pattern_fingerprints",
        )
        accepted_fingerprints = _fingerprint_list(
            validated,
            section="validation",
            field="validated_pattern_fingerprints",
        )

        summaries.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "horizon_minutes": horizon,
                "cell_evidence_fingerprint": _validate_sha256(
                    validated.get("evidence_fingerprint"),
                    field="cell evidence fingerprint",
                ),
                "processed_manifest_sha256": processed_sha,
                "feature_manifest_sha256": feature_manifest_sha,
                "outcome_manifest_sha256": outcome_manifest_sha,
                "discovery_shortlist_count": len(shortlist_fingerprints),
                "discovery_shortlist_fingerprints": list(shortlist_fingerprints),
                "confirmation_frozen_count": len(frozen_fingerprints),
                "confirmation_frozen_fingerprints": list(frozen_fingerprints),
                "validation_accepted_count": len(accepted_fingerprints),
                "validation_accepted_fingerprints": list(accepted_fingerprints),
            }
        )

    if tuple(sorted(by_cell)) != tuple(sorted(EXPECTED_CELLS)):
        raise ValueError("EXP-061 aggregate cell inventory is incomplete or unexpected")
    if len(feature_evidence_fingerprints) != 1:
        raise ValueError("EXP-061 aggregate feature evidence fingerprint is not singular")
    if len(outcome_evidence_fingerprints) != 1:
        raise ValueError("EXP-061 aggregate outcome evidence fingerprint is not singular")

    summaries.sort(
        key=lambda item: (
            str(item["symbol"]),
            str(item["timeframe"]),
            int(item["horizon_minutes"]),
        )
    )
    shortlist_count = sum(
        int(item["discovery_shortlist_count"]) for item in summaries
    )
    frozen_count = sum(
        int(item["confirmation_frozen_count"]) for item in summaries
    )
    accepted_count = sum(
        int(item["validation_accepted_count"]) for item in summaries
    )
    if shortlist_count > MAX_DISCOVERY_SHORTLIST:
        raise ValueError("EXP-061 aggregate discovery shortlist exceeds global cap")
    if frozen_count > MAX_FROZEN_PATTERN_HYPOTHESES:
        raise ValueError("EXP-061 aggregate frozen pattern count exceeds global cap")
    if accepted_count > MAX_FROZEN_PATTERN_HYPOTHESES:
        raise ValueError("EXP-061 aggregate accepted pattern count exceeds global cap")

    evidence: dict[str, object] = {
        "evidence_version": EXP061_AGGREGATE_EVIDENCE_VERSION,
        "evidence_protocol": EXP061_AGGREGATE_EVIDENCE_PROTOCOL,
        "experiment_id": EXPERIMENT_ID,
        "run_contract_version": EXP061_RUN_CONTRACT_VERSION,
        "protocol_fingerprint": protocol_fingerprint(),
        "code_commit": code_commit,
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "feature_evidence_fingerprint": next(iter(feature_evidence_fingerprints)),
        "outcome_evidence_fingerprint": next(iter(outcome_evidence_fingerprints)),
        "expected_cell_count": EXPECTED_CELL_COUNT,
        "verified_cell_count": len(summaries),
        "cells": summaries,
        "discovery_shortlist_count": shortlist_count,
        "confirmation_frozen_count": frozen_count,
        "validation_accepted_count": accepted_count,
        "reserved_robustness_opened": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    evidence["evidence_fingerprint"] = _sha256_bytes(_canonical_json(evidence))
    return evidence


def validate_aggregate_evidence(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("evidence_fingerprint"),
        field="EXP-061 aggregate evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("EXP-061 aggregate evidence fingerprint mismatch")
    if value.get("evidence_version") != EXP061_AGGREGATE_EVIDENCE_VERSION:
        raise ValueError("EXP-061 aggregate evidence version mismatch")
    if value.get("evidence_protocol") != EXP061_AGGREGATE_EVIDENCE_PROTOCOL:
        raise ValueError("EXP-061 aggregate evidence protocol mismatch")
    if value.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("EXP-061 aggregate experiment identity mismatch")
    if value.get("run_contract_version") != EXP061_RUN_CONTRACT_VERSION:
        raise ValueError("EXP-061 aggregate run-contract identity mismatch")
    if value.get("protocol_fingerprint") != protocol_fingerprint():
        raise ValueError("EXP-061 aggregate protocol fingerprint mismatch")
    _validate_commit(value.get("code_commit"))
    if value.get("evidence_label") != "RETROSPECTIVE_ALREADY_SEEN":
        raise ValueError("EXP-061 aggregate evidence label mismatch")
    if value.get("untouched_oos") is not False:
        raise ValueError("EXP-061 aggregate cannot claim untouched OOS")
    if value.get("reserved_robustness_opened") is not False:
        raise ValueError("EXP-061 aggregate cannot open reserved robustness")
    for field in (
        "candidate_compilation_authorized",
        "promotion_authorized",
        "phase8b_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"EXP-061 aggregate {field} must remain false")

    _validate_sha256(
        value.get("feature_evidence_fingerprint"),
        field="feature_evidence_fingerprint",
    )
    _validate_sha256(
        value.get("outcome_evidence_fingerprint"),
        field="outcome_evidence_fingerprint",
    )
    if value.get("expected_cell_count") != EXPECTED_CELL_COUNT:
        raise ValueError("EXP-061 aggregate expected cell count mismatch")
    if value.get("verified_cell_count") != EXPECTED_CELL_COUNT:
        raise ValueError("EXP-061 aggregate verified cell count mismatch")

    cells = value.get("cells")
    if not isinstance(cells, list) or len(cells) != EXPECTED_CELL_COUNT:
        raise ValueError("EXP-061 aggregate cell summaries are incomplete")
    seen: list[tuple[str, str, int]] = []
    shortlist_count = 0
    frozen_count = 0
    accepted_count = 0
    manifests: dict[tuple[str, str], tuple[str, str]] = {}
    for raw in cells:
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-061 aggregate cell summary must be an object")
        identity = (
            raw.get("symbol"),
            raw.get("timeframe"),
            raw.get("horizon_minutes"),
        )
        if identity not in EXPECTED_CELLS:
            raise ValueError(f"unexpected EXP-061 aggregate summary cell: {identity!r}")
        seen.append((str(identity[0]), str(identity[1]), int(identity[2])))
        _validate_sha256(
            raw.get("cell_evidence_fingerprint"),
            field="cell_evidence_fingerprint",
        )
        processed = _validate_sha256(
            raw.get("processed_manifest_sha256"),
            field="processed_manifest_sha256",
        )
        if processed != EXPECTED_SOURCE_MANIFEST_SHA256[str(identity[0])]:
            raise ValueError("EXP-061 aggregate summary source identity mismatch")
        feature_manifest = _validate_sha256(
            raw.get("feature_manifest_sha256"),
            field="feature_manifest_sha256",
        )
        outcome_manifest = _validate_sha256(
            raw.get("outcome_manifest_sha256"),
            field="outcome_manifest_sha256",
        )
        key = (str(identity[0]), str(identity[1]))
        pair = (feature_manifest, outcome_manifest)
        prior = manifests.setdefault(key, pair)
        if prior != pair:
            raise ValueError("EXP-061 aggregate summary manifest identity drift")

        discovery_fps = raw.get("discovery_shortlist_fingerprints")
        frozen_fps = raw.get("confirmation_frozen_fingerprints")
        accepted_fps = raw.get("validation_accepted_fingerprints")
        for field, inventory in (
            ("discovery_shortlist_fingerprints", discovery_fps),
            ("confirmation_frozen_fingerprints", frozen_fps),
            ("validation_accepted_fingerprints", accepted_fps),
        ):
            if not isinstance(inventory, list):
                raise ValueError(f"EXP-061 aggregate {field} must be a list")
            for item in inventory:
                _validate_sha256(item, field=field)
            if len(inventory) != len(set(inventory)):
                raise ValueError(f"EXP-061 aggregate {field} contains duplicates")

        if raw.get("discovery_shortlist_count") != len(discovery_fps):
            raise ValueError("EXP-061 aggregate discovery shortlist count mismatch")
        if raw.get("confirmation_frozen_count") != len(frozen_fps):
            raise ValueError("EXP-061 aggregate confirmation frozen count mismatch")
        if raw.get("validation_accepted_count") != len(accepted_fps):
            raise ValueError("EXP-061 aggregate validation accepted count mismatch")
        if not set(frozen_fps).issubset(set(discovery_fps)):
            raise ValueError("EXP-061 aggregate frozen patterns are not discovery shortlist members")
        if not set(accepted_fps).issubset(set(frozen_fps)):
            raise ValueError("EXP-061 aggregate accepted patterns are not frozen members")

        shortlist_count += len(discovery_fps)
        frozen_count += len(frozen_fps)
        accepted_count += len(accepted_fps)

    if tuple(seen) != tuple(
        sorted(
            EXPECTED_CELLS,
            key=lambda item: (item[0], item[1], item[2]),
        )
    ):
        raise ValueError("EXP-061 aggregate cell summaries are not exact and sorted")
    if value.get("discovery_shortlist_count") != shortlist_count:
        raise ValueError("EXP-061 aggregate total shortlist count mismatch")
    if value.get("confirmation_frozen_count") != frozen_count:
        raise ValueError("EXP-061 aggregate total frozen count mismatch")
    if value.get("validation_accepted_count") != accepted_count:
        raise ValueError("EXP-061 aggregate total accepted count mismatch")
    if shortlist_count > MAX_DISCOVERY_SHORTLIST:
        raise ValueError("EXP-061 aggregate shortlist exceeds global cap")
    if frozen_count > MAX_FROZEN_PATTERN_HYPOTHESES:
        raise ValueError("EXP-061 aggregate frozen count exceeds global cap")
    if accepted_count > MAX_FROZEN_PATTERN_HYPOTHESES:
        raise ValueError("EXP-061 aggregate accepted count exceeds global cap")
    return value


__all__ = [
    "ADAPTER_SOURCE_BLOB_SHA",
    "AGGREGATE_JOB_NAME",
    "DISCOVERY_RESULT_AUTHORIZED",
    "EXPECTED_ARTIFACT_COUNT",
    "EXPECTED_CELL_COUNT",
    "EXPECTED_CELLS",
    "EXPECTED_JOB_COUNT",
    "EXP061_AGGREGATE_EVIDENCE_PROTOCOL",
    "EXP061_AGGREGATE_EVIDENCE_VERSION",
    "EXP061_RUN_CONTRACT_DECISION",
    "EXP061_RUN_CONTRACT_VERSION",
    "HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    "LOADER_SOURCE_BLOB_SHA",
    "MINER_SOURCE_BLOB_SHA",
    "PREFLIGHT_JOB_NAME",
    "PROTOCOL_SOURCE_BLOB_SHA",
    "RERUN_AUTHORIZED",
    "REPLACEMENT_RUN_AUTHORIZED",
    "RETRY_AUTHORIZED",
    "WORKFLOW_DISPATCH_AUTHORIZED",
    "WORKFLOW_NAME",
    "WORKFLOW_PATH",
    "WORKFLOW_RUN_ATTEMPT",
    "compile_aggregate_evidence",
    "expected_artifact_names",
    "expected_cell_artifact_name",
    "expected_cell_job_name",
    "expected_job_names",
    "run_contract_payload",
    "validate_aggregate_evidence",
]
