import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_cli():
    return subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "gate5g",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class Gate5GCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first_run = run_cli()

    def test_cli_reports_expected_governed_evaluation(self):
        self.assertEqual(
            self.first_run.returncode,
            0,
            msg=self.first_run.stderr,
        )
        self.assertEqual(self.first_run.stderr, "")

        result = json.loads(self.first_run.stdout)
        evaluation = result["study1_evaluation"]

        self.assertEqual(result["demo"], "GATE-5G")
        self.assertEqual(
            evaluation["model"],
            "Random Forest first clean run",
        )
        self.assertEqual(
            evaluation["archived_accuracy"],
            0.846939,
        )
        self.assertEqual(
            evaluation["archived_macro_f1"],
            0.653251,
        )
        self.assertEqual(
            evaluation["normal_operation_correct"],
            1,
        )
        self.assertEqual(
            evaluation["normal_operation_records"],
            14,
        )
        self.assertEqual(
            evaluation["normal_operation_recall"],
            0.071429,
        )
        self.assertEqual(
            evaluation["ungoverned_release_state"],
            "DIRECT_MODEL_OUTPUT",
        )
        self.assertEqual(
            evaluation["governed_decision"],
            "ABSTAIN",
        )
        self.assertEqual(
            evaluation["governed_reason_codes"],
            ["CONFIDENCE_THRESHOLDS_MISSING"],
        )
        self.assertFalse(
            evaluation["governed_diagnosis_released"]
        )
        self.assertFalse(
            evaluation["confidence_thresholds_configured"]
        )
        self.assertFalse(
            evaluation["row_level_confidence_replay_performed"]
        )
        self.assertFalse(
            evaluation["original_study_governed"]
        )
        self.assertEqual(
            evaluation["evaluation_scope"],
            "AGGREGATE_POLICY_GATE_ONLY",
        )

    def test_cli_preserves_cross_study_separation(self):
        result = json.loads(self.first_run.stdout)

        self.assertEqual(
            result["study1"],
            {
                "study_id": "study_01_published",
                "data_origin": "STUDY_01",
                "record_count": 462,
            },
        )

        self.assertEqual(
            result["study2"],
            {
                "study_id": "study_02_independent",
                "data_origin": "STUDY_02",
                "record_count": 1400,
            },
        )

        self.assertNotEqual(
            result["study1"]["study_id"],
            result["study2"]["study_id"],
        )
        self.assertNotEqual(
            result["study1"]["data_origin"],
            result["study2"]["data_origin"],
        )

    def test_cli_is_reproducible_and_audit_chain_is_valid(self):
        first = json.loads(self.first_run.stdout)

        self.assertTrue(first["audit"]["chain_valid"])
        self.assertEqual(
            len(first["audit"]["event_hash"]),
            64,
        )

        second_run = run_cli()

        self.assertEqual(
            second_run.returncode,
            0,
            msg=second_run.stderr,
        )
        self.assertEqual(second_run.stderr, "")
        self.assertEqual(
            self.first_run.stdout,
            second_run.stdout,
        )


if __name__ == "__main__":
    unittest.main()