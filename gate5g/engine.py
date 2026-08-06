"""Deterministic GATE-5G governance decision engine."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class Decision(str, Enum):
    ALLOW_DIAGNOSIS = "ALLOW_DIAGNOSIS"
    RECOMMEND_ONLY = "RECOMMEND_ONLY"
    REQUIRE_HUMAN_APPROVAL = "REQUIRE_HUMAN_APPROVAL"
    ABSTAIN = "ABSTAIN"
    BLOCK = "BLOCK"


class Authority(str, Enum):
    L0_OBSERVE = "L0_OBSERVE"
    L1_DIAGNOSE = "L1_DIAGNOSE"
    L2_RECOMMEND = "L2_RECOMMEND"
    L3_APPROVAL_REQUIRED = "L3_APPROVAL_REQUIRED"


_AUTHORITY_RANK = {
    Authority.L0_OBSERVE: 0,
    Authority.L1_DIAGNOSE: 1,
    Authority.L2_RECOMMEND: 2,
    Authority.L3_APPROVAL_REQUIRED: 3,
}


@dataclass(frozen=True)
class GovernanceRequest:
    request_id: str
    study_id: str
    data_origin: str
    policy_version: str
    provenance_valid: bool
    schema_valid: bool
    model_registered: bool
    calibration_status: str
    out_of_distribution: bool
    predicted_class: str
    confidence: Optional[float]
    requested_authority: str


@dataclass(frozen=True)
class GovernanceResponse:
    request_id: str
    study_id: str
    decision: str
    granted_authority: str
    reason_codes: Tuple[str, ...]


def load_governance_config(repo_root: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    root = Path(repo_root)

    with (root / "config" / "gate5g" / "policy_v1.json").open(
        "r", encoding="utf-8"
    ) as policy_file:
        policy = json.load(policy_file)

    with (root / "config" / "gate5g" / "study_registry_v1.json").open(
        "r", encoding="utf-8"
    ) as registry_file:
        registry = json.load(registry_file)

    return policy, registry


def _response(
    request: GovernanceRequest,
    decision: Decision,
    authority: Authority,
    *reason_codes: str,
) -> GovernanceResponse:
    return GovernanceResponse(
        request_id=request.request_id,
        study_id=request.study_id,
        decision=decision.value,
        granted_authority=authority.value,
        reason_codes=tuple(reason_codes),
    )


def _find_study(registry: Dict[str, Any], study_id: str) -> Optional[Dict[str, Any]]:
    for study in registry.get("studies", []):
        if study.get("study_id") == study_id:
            return study
    return None


def _number_in_unit_interval(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and 0.0 <= float(value) <= 1.0
    )


def evaluate_request(
    request: GovernanceRequest,
    policy: Dict[str, Any],
    registry: Dict[str, Any],
) -> GovernanceResponse:
    observe = Authority.L0_OBSERVE

    if request.policy_version != policy.get("policy_version"):
        return _response(request, Decision.BLOCK, observe, "POLICY_UNKNOWN")

    study = _find_study(registry, request.study_id)

    if study is None:
        return _response(request, Decision.BLOCK, observe, "STUDY_UNKNOWN")

    if not request.provenance_valid:
        return _response(request, Decision.BLOCK, observe, "PROVENANCE_MISSING")

    if request.data_origin != study.get("data_origin"):
        return _response(request, Decision.BLOCK, observe, "STUDY_MISMATCH")

    if not request.schema_valid:
        return _response(request, Decision.BLOCK, observe, "SCHEMA_INVALID")

    if not request.model_registered:
        return _response(request, Decision.BLOCK, observe, "MODEL_UNKNOWN")

    if not request.predicted_class.strip():
        return _response(request, Decision.BLOCK, observe, "MODEL_OUTPUT_INVALID")

    try:
        requested_authority = Authority(request.requested_authority)
    except ValueError:
        return _response(request, Decision.BLOCK, observe, "AUTHORITY_INVALID")

    study_policy = policy.get("study_policies", {}).get(request.study_id)

    if not isinstance(study_policy, dict):
        return _response(request, Decision.BLOCK, observe, "POLICY_UNKNOWN")

    try:
        maximum_authority = Authority(study_policy["maximum_authority"])
    except (KeyError, ValueError):
        return _response(request, Decision.BLOCK, observe, "POLICY_INVALID")

    granted_authority = requested_authority
    authority_capped = False

    if _AUTHORITY_RANK[requested_authority] > _AUTHORITY_RANK[maximum_authority]:
        granted_authority = maximum_authority
        authority_capped = True

    if request.out_of_distribution:
        return _response(
            request,
            Decision.ABSTAIN,
            granted_authority,
            "OUT_OF_DISTRIBUTION",
        )

    registry_calibration = study.get("calibration_state")

    if registry_calibration is not None and registry_calibration != "COMPLETE":
        return _response(
            request,
            Decision.ABSTAIN,
            granted_authority,
            "STUDY2_INCOMPLETE",
        )

    if request.calibration_status != "COMPLETE":
        return _response(
            request,
            Decision.ABSTAIN,
            granted_authority,
            "CALIBRATION_MISSING",
        )

    thresholds = study_policy.get("confidence_thresholds")

    if not isinstance(thresholds, dict):
        return _response(
            request,
            Decision.ABSTAIN,
            granted_authority,
            "CONFIDENCE_THRESHOLDS_MISSING",
        )

    review_threshold = thresholds.get("review")
    accept_threshold = thresholds.get("accept")

    if (
        not _number_in_unit_interval(review_threshold)
        or not _number_in_unit_interval(accept_threshold)
        or float(review_threshold) > float(accept_threshold)
    ):
        return _response(request, Decision.BLOCK, observe, "POLICY_INVALID")

    if request.confidence is None:
        return _response(
            request,
            Decision.ABSTAIN,
            granted_authority,
            "CONFIDENCE_MISSING",
        )

    if not _number_in_unit_interval(request.confidence):
        return _response(
            request,
            Decision.BLOCK,
            observe,
            "MODEL_OUTPUT_INVALID",
        )

    if request.confidence < float(review_threshold):
        return _response(
            request,
            Decision.ABSTAIN,
            granted_authority,
            "CONFIDENCE_INSUFFICIENT",
        )

    reasons = []

    if authority_capped:
        reasons.append("AUTHORITY_CAPPED")

    if request.confidence < float(accept_threshold):
        reasons.append("CONFIDENCE_REVIEW_REQUIRED")
        reasons.append("HUMAN_APPROVAL_REQUIRED")
        return _response(
            request,
            Decision.REQUIRE_HUMAN_APPROVAL,
            granted_authority,
            *reasons,
        )

    reasons.append("CONFIDENCE_ACCEPTED")

    if granted_authority == Authority.L2_RECOMMEND:
        return _response(
            request,
            Decision.RECOMMEND_ONLY,
            granted_authority,
            *reasons,
        )

    if granted_authority == Authority.L3_APPROVAL_REQUIRED:
        reasons.append("HUMAN_APPROVAL_REQUIRED")
        return _response(
            request,
            Decision.REQUIRE_HUMAN_APPROVAL,
            granted_authority,
            *reasons,
        )

    return _response(
        request,
        Decision.ALLOW_DIAGNOSIS,
        granted_authority,
        *reasons,
    )