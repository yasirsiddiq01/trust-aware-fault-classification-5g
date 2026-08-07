import unittest
from pathlib import Path

from gate5g.engine import (
    Authority,
    Decision,
    GovernanceRequest,
    evaluate_request,
    load_governance_config,
)
from gate5g.study1_adapter import load_study1_records
from gate5g.study2_adapter import load_study2_records


REPO_ROOT = Path(__file__).resolve().parents[1]


class CrossStudyIsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy, cls.registry = load_governance_config(REPO_ROOT)
        cls.study1_records = load_study1_records(REPO_ROOT)
        cls.study2_records = load_study2_records(REPO_ROOT)

    def request(self, study_id, data_origin):
        return GovernanceRequest(
            request_id="ISOLATION-001",
            study_id=study_id,
            data_origin=data_origin,
            policy_version=self.policy["policy_version"],
            provenance_valid=True,
            schema_valid=True,
            model_registered=True,
            calibration_status="COMPLETE",
            out_of_distribution=False,
            predicted_class="radio_degradation",
            confidence=0.90,
            requested_authority=Authority.L1_DIAGNOSE.value,
        )

    def test_registry_prohibits_cross_study_data_and_paths_are_disjoint(self):
        studies = {
            study["study_id"]: study
            for study in self.registry["studies"]
        }

        study1 = studies["study_01_published"]
        study2 = studies["study_02_independent"]

        self.assertFalse(study1["cross_study_data_allowed"])
        self.assertFalse(study2["cross_study_data_allowed"])

        study1_paths = set(study1["repository_paths"])
        study2_paths = set(study2["repository_paths"])

        self.assertTrue(study1_paths.isdisjoint(study2_paths))
        self.assertEqual(
            study2["relationship_to_study_01"],
            "RESEARCH_LINEAGE_ONLY",
        )

    def test_adapter_outputs_are_cross_study_disjoint(self):
        self.assertTrue(
            all(
                record.study_id == "study_01_published"
                and record.data_origin == "STUDY_01"
                for record in self.study1_records
            )
        )

        self.assertTrue(
            all(
                record.study_id == "study_02_independent"
                and record.data_origin == "STUDY_02"
                for record in self.study2_records
            )
        )

        study1_references = {
            record.evidence_reference
            for record in self.study1_records
        }
        study2_references = {
            record.evidence_reference
            for record in self.study2_records
        }

        self.assertTrue(
            study1_references.isdisjoint(study2_references)
        )

        self.assertTrue(
            all(
                "study_02_independent" not in reference
                for reference in study1_references
            )
        )

        self.assertTrue(
            all(
                "study_01_published" not in reference
                for reference in study2_references
            )
        )

    def test_study1_request_rejects_study2_origin(self):
        response = evaluate_request(
            self.request(
                study_id="study_01_published",
                data_origin="STUDY_02",
            ),
            self.policy,
            self.registry,
        )

        self.assertEqual(response.decision, Decision.BLOCK.value)
        self.assertEqual(
            response.granted_authority,
            Authority.L0_OBSERVE.value,
        )
        self.assertEqual(
            response.reason_codes,
            ("STUDY_MISMATCH",),
        )

    def test_study2_request_rejects_study1_origin(self):
        response = evaluate_request(
            self.request(
                study_id="study_02_independent",
                data_origin="STUDY_01",
            ),
            self.policy,
            self.registry,
        )

        self.assertEqual(response.decision, Decision.BLOCK.value)
        self.assertEqual(
            response.granted_authority,
            Authority.L0_OBSERVE.value,
        )
        self.assertEqual(
            response.reason_codes,
            ("STUDY_MISMATCH",),
        )


if __name__ == "__main__":
    unittest.main()
