import tempfile
import unittest
from pathlib import Path

from gate5g.engine import Authority, Decision
from gate5g.study1_evaluation import (
    ARCHIVED_MODEL_NAME,
    EVALUATION_SCOPE,
    RESULTS_RELATIVE_PATH,
    UNGOVERNED_RELEASE_STATE,
    Study1EvaluationError,
    evaluate_study1_retrospective,
    load_archived_study1_snapshot,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class Study1RetrospectiveEvaluationTests(unittest.TestCase):
    def test_archived_snapshot_matches_frozen_results(self):
        snapshot = load_archived_study1_snapshot(REPO_ROOT)

        self.assertEqual(snapshot.model_name, ARCHIVED_MODEL_NAME)
        self.assertEqual(snapshot.accuracy, 0.846939)
        self.assertEqual(snapshot.macro_f1, 0.653251)

        self.assertEqual(snapshot.normal_operation_records, 14)
        self.assertEqual(snapshot.normal_operation_correct, 1)
        self.assertEqual(
            snapshot.normal_operation_predicted_radio_degradation,
            13,
        )
        self.assertEqual(snapshot.normal_operation_recall, 0.071429)

        self.assertEqual(
            snapshot.source_reference,
            RESULTS_RELATIVE_PATH.as_posix(),
        )

    def test_current_governance_fails_closed_without_thresholds(self):
        result = evaluate_study1_retrospective(REPO_ROOT)

        self.assertEqual(
            result.ungoverned_release_state,
            UNGOVERNED_RELEASE_STATE,
        )

        self.assertEqual(
            result.governed_decision,
            Decision.ABSTAIN.value,
        )

        self.assertEqual(
            result.governed_granted_authority,
            Authority.L1_DIAGNOSE.value,
        )

        self.assertEqual(
            result.governed_reason_codes,
            ("CONFIDENCE_THRESHOLDS_MISSING",),
        )

        self.assertFalse(result.governed_diagnosis_released)
        self.assertFalse(result.confidence_thresholds_configured)

    def test_evaluation_declares_bounded_retrospective_scope(self):
        result = evaluate_study1_retrospective(REPO_ROOT)

        self.assertEqual(
            result.evaluation_scope,
            EVALUATION_SCOPE,
        )

        self.assertFalse(
            result.row_level_confidence_replay_performed
        )

        self.assertFalse(result.original_study_governed)

    def test_missing_archived_results_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(
                Study1EvaluationError,
                "results document is missing",
            ):
                load_archived_study1_snapshot(
                    Path(temporary_directory)
                )

    def test_same_repository_state_produces_same_evaluation(self):
        first = evaluate_study1_retrospective(REPO_ROOT)
        second = evaluate_study1_retrospective(REPO_ROOT)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
