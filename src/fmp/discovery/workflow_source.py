from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .run_contract import (
    EXPECTED_CELLS,
    expected_aggregate_artifact_name,
    expected_cell_artifact_name,
    expected_job_names,
    expected_preflight_artifact_name,
    run_contract_payload,
)


EXP061_DORMANT_WORKFLOW_SOURCE_DECISION = "DEC-275"
EXP061_DORMANT_WORKFLOW_SOURCE_VERSION = "fmp-exp061-dormant-workflow-source-v1"

DORMANT_WORKFLOW_TEMPLATE_PATH = (
    "docs/superpowers/templates/phase8a-exp061-discovery.yml.disabled"
)
RESERVED_ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-exp061-discovery.yml"

FEATURE_RUN = {
    "id": 35867307338,
    "name": "phase8a-exp044-market-features",
    "path": ".github/workflows/phase8a-exp044-market-features.yml",
    "event": "workflow_dispatch",
    "head_branch": "main",
    "head_sha": "b71912e254d2a597c0ef55b5e1b3b87b052039ea",
    "run_attempt": 1,
    "status": "completed",
    "conclusion": "success",
}
OUTCOME_RUN = {
    "id": 35876715434,
    "name": "phase8a-exp044-market-outcomes",
    "path": ".github/workflows/phase8a-exp044-market-outcomes.yml",
    "event": "workflow_dispatch",
    "head_branch": "main",
    "head_sha": "edeb43bb4de88923e3349caa8ace36350839ccb8",
    "run_attempt": 1,
    "status": "completed",
    "conclusion": "success",
}

FEATURE_EVIDENCE_ARTIFACT = {
    "id": 10753455784,
    "name": "exp044-market-feature-evidence-b71912e254d2a597c0ef55b5e1b3b87b052039ea",
    "digest": "sha256:1d3763c3d8ef13ba5157786c019349f1a7fdb22d626800fbc5b41ad779448f04",
}
OUTCOME_EVIDENCE_ARTIFACT = {
    "id": 10758027876,
    "name": (
        "exp044-market-outcome-evidence-"
        "edeb43bb4de88923e3349caa8ace36350839ccb8-"
        "from-b71912e254d2a597c0ef55b5e1b3b87b052039ea"
    ),
    "digest": "sha256:3c360629c8a408e6b0f97ee9c1254ca936c0144964fd1bb74855f394230a4d05",
}

_CELL_SOURCE_ARTIFACTS = {
    ("EURUSD", "5m"): {
        "feature_id": 10752009633,
        "feature_digest": "sha256:a466f0a128ea8cdc5818c6756bb71a57767f0c703eec68ad40a680f1bf9b06e2",
        "outcome_id": 10759485253,
        "outcome_digest": "sha256:243824ecfb365a94dbe49442352440ffc3730240b4ca9758b0b94d8e6224534b",
    },
    ("EURUSD", "15m"): {
        "feature_id": 10753305695,
        "feature_digest": "sha256:a942b0bf97995cd67e94335435ab3c06ee0da7688f5ac494b79470c1c637b4ee",
        "outcome_id": 10759375276,
        "outcome_digest": "sha256:dca7f656c08e7b35c51e3549cdcaf92849b2905d70cbeecc5ff1ed3773eeedd0",
    },
    ("EURUSD", "1h"): {
        "feature_id": 10753555531,
        "feature_digest": "sha256:831a1957519714933cc34c12fe126a88aeaf7fa9a359be6399b8569a236ee59e",
        "outcome_id": 10759490258,
        "outcome_digest": "sha256:4594975177b8f7b0ff2979ddba85b774d55b65afe3da61491226dc0bb6f1eaf4",
    },
    ("GBPUSD", "5m"): {
        "feature_id": 10753690116,
        "feature_digest": "sha256:62bb96d9492fa092cd5aa157223be34dab6c78fb20e381a4d7804adbcec22498",
        "outcome_id": 10759375400,
        "outcome_digest": "sha256:69b5a774707fe1bf26e271ad6a89084f22169a9155dc5debcbf5d00c00a2fdf4",
    },
    ("GBPUSD", "15m"): {
        "feature_id": 10753680126,
        "feature_digest": "sha256:c5d894f595e85f84670ac66348b0fb40366a80286408c8c1b777549a5dffdc84",
        "outcome_id": 10759695313,
        "outcome_digest": "sha256:a04e9a5ffa5faaf8200385fe7a71bf1d9a56aba3021d60bae25c247b537c365f",
    },
    ("GBPUSD", "1h"): {
        "feature_id": 10753440747,
        "feature_digest": "sha256:f7c66064a0255585ecf5e4eca6da86bbea3eee58d38bbf9aaeecd04748a8f6f8",
        "outcome_id": 10759645383,
        "outcome_digest": "sha256:b2a192ceca9031dc2460194db698318a04b99df9f346b4c32c8e9ba7803d4f49",
    },
    ("USDJPY", "5m"): {
        "feature_id": 10752846673,
        "feature_digest": "sha256:d719b40919b1edf1f868352c19579f30528232387df3862c7f85782d8a2a7360",
        "outcome_id": 10757827671,
        "outcome_digest": "sha256:42794311c61189b95a130efafab50cc2c9586d00761e053727f7a05ecd66e36f",
    },
    ("USDJPY", "15m"): {
        "feature_id": 10753781465,
        "feature_digest": "sha256:5fdec186a2e086e725623682fd8143294d941635a780038070904e15ed2a4a92",
        "outcome_id": 10757812657,
        "outcome_digest": "sha256:edc30a8f49b072e6504a82ae0d90d30a1a362b4dd825bf48d0ed1d2b567af2be",
    },
    ("USDJPY", "1h"): {
        "feature_id": 10752752044,
        "feature_digest": "sha256:bc8936d2a02bfc6cde9d11eae23330bfc047374f03fe265ed15eaa6d4d0bd3b4",
        "outcome_id": 10757692733,
        "outcome_digest": "sha256:aa7fda1ca6e43c3b41a2ee1fb3729de61bb7dc6ea55e98fda70e8434770a8ee4",
    },
}

WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED = False
WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


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


def _validate_sha256_digest(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise ValueError(f"{field} must use sha256:<hex>")
    raw = value.removeprefix("sha256:")
    if len(raw) != 64:
        raise ValueError(f"{field} must contain 64 hex characters")
    try:
        int(raw, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def _validate_commit(value: object) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError("code_commit must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError("code_commit must be hexadecimal") from exc
    return value


def source_artifacts_for_cell(
    symbol: str,
    timeframe: str,
) -> Mapping[str, object]:
    key = (symbol, timeframe)
    if key not in _CELL_SOURCE_ARTIFACTS:
        raise ValueError("unsupported EXP-061 source cell")
    return dict(_CELL_SOURCE_ARTIFACTS[key])


def _validate_run_snapshot(
    value: Mapping[str, object],
    expected: Mapping[str, object],
    *,
    label: str,
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"{label} run {field} mismatch")


def _artifact_by_id(
    artifacts_payload: Mapping[str, object],
) -> dict[int, Mapping[str, object]]:
    raw = artifacts_payload.get("artifacts")
    if not isinstance(raw, list):
        raise ValueError("source artifact payload must contain an artifacts list")
    by_id: dict[int, Mapping[str, object]] = {}
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("source artifact row must be an object")
        artifact_id = item.get("id")
        if not isinstance(artifact_id, int) or isinstance(artifact_id, bool):
            raise ValueError("source artifact id must be an integer")
        if artifact_id in by_id:
            raise ValueError("source artifact id is duplicated")
        by_id[artifact_id] = item
    return by_id


def _validate_artifact(
    by_id: Mapping[int, Mapping[str, object]],
    expected: Mapping[str, object],
    *,
    label: str,
) -> None:
    artifact_id = expected.get("id")
    if not isinstance(artifact_id, int):
        raise ValueError(f"{label} expected artifact id is invalid")
    row = by_id.get(artifact_id)
    if row is None:
        raise ValueError(f"{label} expected artifact is missing")
    if row.get("name") != expected.get("name"):
        raise ValueError(f"{label} artifact name mismatch")
    if row.get("expired") is not False:
        raise ValueError(f"{label} artifact must be non-expired")
    digest = _validate_sha256_digest(
        row.get("digest"),
        field=f"{label} artifact digest",
    )
    if digest != expected.get("digest"):
        raise ValueError(f"{label} artifact digest mismatch")


def _cell_expected_artifacts() -> tuple[dict[str, object], ...]:
    out: list[dict[str, object]] = []
    for symbol, timeframe in sorted(_CELL_SOURCE_ARTIFACTS):
        raw = _CELL_SOURCE_ARTIFACTS[(symbol, timeframe)]
        feature_head = FEATURE_RUN["head_sha"]
        outcome_head = OUTCOME_RUN["head_sha"]
        out.append(
            {
                "label": f"feature {symbol} {timeframe}",
                "run": "feature",
                "id": raw["feature_id"],
                "digest": raw["feature_digest"],
                "name": (
                    f"exp044-market-features-{symbol}-{timeframe}-"
                    f"{feature_head}"
                ),
            }
        )
        out.append(
            {
                "label": f"outcome {symbol} {timeframe}",
                "run": "outcome",
                "id": raw["outcome_id"],
                "digest": raw["outcome_digest"],
                "name": (
                    f"exp044-market-outcomes-{symbol}-{timeframe}-"
                    f"{outcome_head}-from-{feature_head}"
                ),
            }
        )
    return tuple(out)


def validate_source_snapshots(
    *,
    feature_run: Mapping[str, object],
    feature_artifacts: Mapping[str, object],
    outcome_run: Mapping[str, object],
    outcome_artifacts: Mapping[str, object],
) -> dict[str, object]:
    _validate_run_snapshot(feature_run, FEATURE_RUN, label="EXP-044 feature")
    _validate_run_snapshot(outcome_run, OUTCOME_RUN, label="EXP-044 outcome")
    feature_by_id = _artifact_by_id(feature_artifacts)
    outcome_by_id = _artifact_by_id(outcome_artifacts)

    _validate_artifact(
        feature_by_id,
        FEATURE_EVIDENCE_ARTIFACT,
        label="EXP-044 feature evidence",
    )
    _validate_artifact(
        outcome_by_id,
        OUTCOME_EVIDENCE_ARTIFACT,
        label="EXP-044 outcome evidence",
    )
    for expected in _cell_expected_artifacts():
        target = feature_by_id if expected["run"] == "feature" else outcome_by_id
        _validate_artifact(
            target,
            expected,
            label=str(expected["label"]),
        )

    report: dict[str, object] = {
        "decision": EXP061_DORMANT_WORKFLOW_SOURCE_DECISION,
        "source_version": EXP061_DORMANT_WORKFLOW_SOURCE_VERSION,
        "feature_run_id": FEATURE_RUN["id"],
        "feature_head_sha": FEATURE_RUN["head_sha"],
        "outcome_run_id": OUTCOME_RUN["id"],
        "outcome_head_sha": OUTCOME_RUN["head_sha"],
        "feature_evidence_artifact_id": FEATURE_EVIDENCE_ARTIFACT["id"],
        "outcome_evidence_artifact_id": OUTCOME_EVIDENCE_ARTIFACT["id"],
        "verified_pair_timeframe_source_count": len(_CELL_SOURCE_ARTIFACTS),
        "source_ready": True,
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
        "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
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
    }
    report["source_fingerprint"] = _sha256_bytes(_canonical_json(report))
    return report


def require_historical_execution_authorized(*, code_commit: str) -> None:
    _validate_commit(code_commit)
    if not HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED:
        raise PermissionError(
            "DEC-275 historical EXP-061 discovery execution remains locked"
        )


def workflow_source_payload(*, code_commit: str) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    return {
        "decision": EXP061_DORMANT_WORKFLOW_SOURCE_DECISION,
        "source_version": EXP061_DORMANT_WORKFLOW_SOURCE_VERSION,
        "code_commit": code_commit,
        "dormant_template_path": DORMANT_WORKFLOW_TEMPLATE_PATH,
        "reserved_active_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "template_install_authorized": WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED,
        "workflow_dispatch_authorized": WORKFLOW_DISPATCH_AUTHORIZED,
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
        "feature_source_run": dict(FEATURE_RUN),
        "outcome_source_run": dict(OUTCOME_RUN),
        "feature_evidence_artifact": dict(FEATURE_EVIDENCE_ARTIFACT),
        "outcome_evidence_artifact": dict(OUTCOME_EVIDENCE_ARTIFACT),
        "pair_timeframe_source_artifacts": [
            {
                "symbol": symbol,
                "timeframe": timeframe,
                **dict(_CELL_SOURCE_ARTIFACTS[(symbol, timeframe)]),
            }
            for symbol, timeframe in sorted(_CELL_SOURCE_ARTIFACTS)
        ],
        "expected_job_names": list(expected_job_names()),
        "expected_preflight_artifact": expected_preflight_artifact_name(
            code_commit=code_commit
        ),
        "expected_cell_artifacts": [
            expected_cell_artifact_name(
                symbol,
                timeframe,
                horizon,
                code_commit=code_commit,
            )
            for symbol, timeframe, horizon in EXPECTED_CELLS
        ],
        "expected_aggregate_artifact": expected_aggregate_artifact_name(
            code_commit=code_commit
        ),
        "run_contract": run_contract_payload(code_commit=code_commit),
        "authorizations": {
            "template_install_authorized": WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED,
            "workflow_dispatch_authorized": WORKFLOW_DISPATCH_AUTHORIZED,
            "historical_discovery_execution_authorized": (
                HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
            ),
            "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
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


def validate_dormant_workflow_template(text: str) -> None:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("DEC-275 dormant workflow template must be non-empty")
    if "name: phase8a-exp061-discovery" not in text:
        raise ValueError("DEC-275 dormant workflow name mismatch")
    if "workflow_dispatch:" not in text:
        raise ValueError("DEC-275 dormant workflow trigger mismatch")
    if "matrix:" not in text:
        raise ValueError("DEC-275 dormant workflow must use the frozen cell matrix")
    if "name: exp061-cell-${{ matrix.dataset.symbol }}-${{ matrix.dataset.timeframe }}-${{ matrix.dataset.horizon }}m" not in text:
        raise ValueError("DEC-275 dormant workflow explicit cell name expression missing")
    if "python scripts/phase8a_exp061.py guard-first-run" not in text:
        raise ValueError("EXP-061 workflow first-run guard is missing")
    if "python scripts/phase8a_exp061.py require-execution" not in text:
        raise ValueError("DEC-275 dormant workflow execution gate is missing")
    if text.index("python scripts/phase8a_exp061.py guard-first-run") > text.index(
        "python scripts/phase8a_exp061.py require-execution"
    ):
        raise ValueError("EXP-061 first-run guard must precede execution authorization")
    for job_name in ("exp061-preflight", "exp061-aggregate"):
        if f"name: {job_name}" not in text:
            raise ValueError(f"DEC-275 dormant workflow missing job name {job_name}")
    if "${{ matrix }}" in text:
        raise ValueError("DEC-275 dormant workflow may not use implicit matrix names")


def load_and_validate_dormant_workflow_template(path: Path) -> str:
    text = Path(path).read_text(encoding="utf-8")
    validate_dormant_workflow_template(text)
    return text


__all__ = [
    "CANDIDATE_COMPILATION_AUTHORIZED",
    "DEMO_ORDER_AUTHORIZED",
    "DISCOVERY_RESULT_AUTHORIZED",
    "DORMANT_WORKFLOW_TEMPLATE_PATH",
    "EXP061_DORMANT_WORKFLOW_SOURCE_DECISION",
    "EXP061_DORMANT_WORKFLOW_SOURCE_VERSION",
    "FEATURE_EVIDENCE_ARTIFACT",
    "FEATURE_RUN",
    "HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "OUTCOME_EVIDENCE_ARTIFACT",
    "OUTCOME_RUN",
    "PHASE8B_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "RESERVED_ACTIVE_WORKFLOW_PATH",
    "RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "WORKFLOW_DISPATCH_AUTHORIZED",
    "WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED",
    "load_and_validate_dormant_workflow_template",
    "require_historical_execution_authorized",
    "source_artifacts_for_cell",
    "validate_dormant_workflow_template",
    "validate_source_snapshots",
    "workflow_source_payload",
]
