"""Bounded retrospective governed-vs-ungoverned Study 1 evaluation.

This module does not reproduce the historical model, execute the frozen
notebook, invent confidence values, or calibrate thresholds. It compares
preserved aggregate Study 1 model evidence with the current GATE-5G
policy-gate response.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from gate5g.engine import (
    Authority,
    GovernanceRequest,
    evaluate_request,
    load_governance_config,
)


STUDY_ID = "study_01_published"
DATA_ORIGIN = "STUDY_01"

ARCHIVED_MODEL_NAME = "Random Forest first clean run"

RESULTS_RELATIVE_PATH = (
    Path("docs")
    / "study_01_published"
    / "results.md"
)

EVALUATION_SCOPE = "AGGREGATE_POLICY_GATE_ONLY"
UNGOVERNED_RELEASE_STATE = "DIRECT_MODEL_OUTPUT"


class Study1EvaluationError(RuntimeError):
    """Raised when the bounded Study 1 evaluation contract is violated."""


@dataclass(frozen=True)
class ArchivedStudy1Snapshot:
    """Preserved aggregate evidence for the selected Study 1 model."""

    model_name: str
    accuracy: float
    macro_f1: float
    normal_operation_records: int
    normal_operation_correct: int
    normal_operation_predicted_radio_degradation: int
    normal_operation_recall: float
    source_reference: str


@dataclass(frozen=True)
class Study1GovernanceComparison:
    """Bounded comparison of direct model output and current governance."""

    archived: ArchivedStudy1Snapshot
    ungoverned_release_state: str
    governed_decision: str
    governed_granted_authority: str
    governed_reason_codes: Tuple[str, ...]
    governed_diagnosis_released: bool
    confidence_thresholds_configured: bool
    row_level_confidence_replay_performed: bool
    original_study_governed: bool
    evaluation_scope: str


def _required_match(
    pattern: str,
    text: str,
    label: str,
    flags: int = 0,
) -> re.Match[str]:
    match = re.search(pattern, text, flags)

    if match is None:
        raise Study1EvaluationError(
            f"Required archived Study 1 evidence is missing: {label}"
        )

    return match


def load_archived_study1_snapshot(
    repo_root: Path,
) -> ArchivedStudy1Snapshot:
    """Read the frozen documented Random Forest aggregate results."""

    root = Path(repo_root)
    results_path = root / RESULTS_RELATIVE_PATH

    if not results_path.is_file():
        raise Study1EvaluationError(
            "Archived Study 1 results document is missing."
        )

    text = results_path.read_text(encoding="utf-8")

    model_row = _required_match(
        r"\|\s*Random Forest first clean run\s*"
        r"\|\s*([0-9.]+)\s*"
        r"\|\s*([0-9.]+)\s*\|",
        text,
        "Random Forest model-level results",
    )

    rf_section = _required_match(
        r"### Random Forest first clean run"
        r"(?P<body>.*?)"
        r"(?=\n### |\n## |\Z)",
        text,
        "Random Forest normal-operation section",
        re.DOTALL,
    ).group("body")

    normal_records = _required_match(
        r"normal-operation test records:\s*(\d+);",
        rf_section,
        "normal-operation record count",
    )

    normal_correct = _required_match(
        r"correctly classified as normal:\s*(\d+);",
        rf_section,
        "normal-operation correct count",
    )

    normal_predicted_radio = _required_match(
        r"classified as radio degradation:\s*(\d+);",
        rf_section,
        "normal-operation radio-degradation error count",
    )

    normal_recall = _required_match(
        r"normal-operation recall:\s*([0-9]+(?:\.[0-9]+)?)",
        rf_section,
        "normal-operation recall",
    )

    return ArchivedStudy1Snapshot(
        model_name=ARCHIVED_MODEL_NAME,
        accuracy=float(model_row.group(1)),
        macro_f1=float(model_row.group(2)),
        normal_operation_records=int(normal_records.group(1)),
        normal_operation_correct=int(normal_correct.group(1)),
        normal_operation_predicted_radio_degradation=int(
            normal_predicted_radio.group(1)
        ),
        normal_operation_recall=float(normal_recall.group(1)),
        source_reference=RESULTS_RELATIVE_PATH.as_posix(),
    )


def evaluate_study1_retrospective(
    repo_root: Path,
) -> Study1GovernanceComparison:
    """Evaluate current GATE-5G release control over frozen Study 1 evidence.

    The governance request is a controlled policy-gate probe. Upstream
    validity conditions are set valid so the current Study 1 confidence-policy
    state can be observed. No claim is made that these controls existed in the
    original Study 1 experiment.
    """

    root = Path(repo_root)
    archived = load_archived_study1_snapshot(root)

    policy, registry = load_governance_config(root)

    study_policy = policy.get("study_policies", {}).get(STUDY_ID)

    if not isinstance(study_policy, dict):
        raise Study1EvaluationError(
            "Study 1 governance policy is missing."
        )

    thresholds = study_policy.get("confidence_thresholds")

    if thresholds is not None:
        raise Study1EvaluationError(
            "This bounded evaluation requires Study 1 confidence "
            "thresholds to remain unconfigured. A calibrated threshold "
            "evaluation requires a separately justified methodology."
        )

    request = GovernanceRequest(
        request_id="STUDY1-RETROSPECTIVE-GATE",
        study_id=STUDY_ID,
        data_origin=DATA_ORIGIN,
        policy_version=policy["policy_version"],
        provenance_valid=True,
        schema_valid=True,
        model_registered=True,
        calibration_status="COMPLETE",
        out_of_distribution=False,
        predicted_class="radio_degradation",
        confidence=None,
        requested_authority=Authority.L1_DIAGNOSE.value,
    )

    response = evaluate_request(
        request,
        policy,
        registry,
    )

    return Study1GovernanceComparison(
        archived=archived,
        ungoverned_release_state=UNGOVERNED_RELEASE_STATE,
        governed_decision=response.decision,
        governed_granted_authority=response.granted_authority,
        governed_reason_codes=response.reason_codes,
        governed_diagnosis_released=(
            response.decision == "ALLOW_DIAGNOSIS"
        ),
        confidence_thresholds_configured=False,
        row_level_confidence_replay_performed=False,
        original_study_governed=False,
        evaluation_scope=EVALUATION_SCOPE,
    )
