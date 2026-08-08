"""Reproducible command-line demonstration for GATE-5G."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from gate5g.audit import append_audit_event, verify_audit_chain
from gate5g.study1_adapter import (
    DATA_ORIGIN as STUDY1_DATA_ORIGIN,
    STUDY_ID as STUDY1_ID,
    load_study1_records,
)
from gate5g.study1_evaluation import evaluate_study1_retrospective
from gate5g.study2_adapter import (
    DATA_ORIGIN as STUDY2_DATA_ORIGIN,
    STUDY_ID as STUDY2_ID,
    load_study2_records,
)


def _build_demo(repo_root: Path) -> Dict[str, Any]:
    """Build the deterministic, read-only GATE-5G demonstration."""

    study1_records = load_study1_records(repo_root)
    study2_records = load_study2_records(repo_root)
    comparison = evaluate_study1_retrospective(repo_root)

    audit_event = append_audit_event(
        {
            "event_type": "STUDY1_GOVERNANCE_EVALUATION",
            "study_id": STUDY1_ID,
            "decision": comparison.governed_decision,
            "reason_codes": list(comparison.governed_reason_codes),
            "evaluation_scope": comparison.evaluation_scope,
        }
    )

    return {
        "demo": "GATE-5G",
        "study1": {
            "study_id": STUDY1_ID,
            "data_origin": STUDY1_DATA_ORIGIN,
            "record_count": len(study1_records),
        },
        "study2": {
            "study_id": STUDY2_ID,
            "data_origin": STUDY2_DATA_ORIGIN,
            "record_count": len(study2_records),
        },
        "study1_evaluation": {
            "model": comparison.archived.model_name,
            "archived_accuracy": comparison.archived.accuracy,
            "archived_macro_f1": comparison.archived.macro_f1,
            "normal_operation_correct": (
                comparison.archived.normal_operation_correct
            ),
            "normal_operation_records": (
                comparison.archived.normal_operation_records
            ),
            "normal_operation_recall": (
                comparison.archived.normal_operation_recall
            ),
            "ungoverned_release_state": (
                comparison.ungoverned_release_state
            ),
            "governed_decision": comparison.governed_decision,
            "governed_reason_codes": list(
                comparison.governed_reason_codes
            ),
            "governed_diagnosis_released": (
                comparison.governed_diagnosis_released
            ),
            "confidence_thresholds_configured": (
                comparison.confidence_thresholds_configured
            ),
            "row_level_confidence_replay_performed": (
                comparison.row_level_confidence_replay_performed
            ),
            "original_study_governed": (
                comparison.original_study_governed
            ),
            "evaluation_scope": comparison.evaluation_scope,
        },
        "audit": {
            "chain_valid": verify_audit_chain((audit_event,)),
            "event_hash": audit_event["event_hash"],
        },
    }


def main() -> None:
    """Run the read-only demonstration and print deterministic JSON."""

    repo_root = Path(__file__).resolve().parents[1]
    result = _build_demo(repo_root)

    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()