import copy
import unittest
from dataclasses import replace
from pathlib import Path

from gate5g.engine import (
    Authority,
    Decision,
    GovernanceRequest,
    evaluate_request,
    load_governance_config,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class GovernanceEngineTests(unittest.TestCase):
    def setUp(self):
        policy, registry = load_governance_config(REPO_ROOT)
        self.policy = copy.deepcopy(policy)
        self.registry = copy.deepcopy(registry)

        self.policy["study_policies"]["study_01_published"][
            "confidence_thresholds"
        ] = {"review": 0.60, "accept": 0.80}

        self.policy["study_policies"]["study_02_independent"][
            "confidence_thresholds"
        ] = {"review": 0.60, "accept": 0.80}

        for study in self.registry["studies"]:
            if study["study_id"] == "study_02_independent":
                study["calibration_state"] = "COMPLETE"

    def request(self, **changes):
        values = {
            "request_id": "REQ-001",
            "study_id": "study_01_published",
            "data_origin": "STUDY_01",
            "policy_version": "1.0.0",
            "provenance_valid": True,
            "schema_valid": True,
            "model_registered": True,
            "calibration_status": "COMPLETE",
            "out_of_distribution": False,
            "predicted_class": "radio_degradation",
            "confidence": 0.90,
            "requested_authority": Authority.L1_DIAGNOSE.value,
        }
        values.update(changes)
        return GovernanceRequest(**values)

    def test_invalid_provenance_blocks(self):
        response = evaluate_request(
            self.request(provenance_valid=False),
            self.policy,
            self.registry,
        )
        self.assertEqual(response.decision, Decision.BLOCK.value)
        self.assertEqual(response.reason_codes, ("PROVENANCE_MISSING",))

    def test_study_mismatch_blocks(self):
        response = evaluate_request(
            self.request(data_origin="STUDY_02"),
            self.policy,
            self.registry,
        )
        self.assertEqual(response.decision, Decision.BLOCK.value)
        self.assertEqual(response.reason_codes, ("STUDY_MISMATCH",))

    def test_missing_calibration_abstains(self):
        response = evaluate_request(
            self.request(calibration_status="INCOMPLETE"),
            self.policy,
            self.registry,
        )
        self.assertEqual(response.decision, Decision.ABSTAIN.value)
        self.assertEqual(response.reason_codes, ("CALIBRATION_MISSING",))

    def test_repository_policy_without_thresholds_abstains(self):
        policy, registry = load_governance_config(REPO_ROOT)
        response = evaluate_request(self.request(), policy, registry)
        self.assertEqual(response.decision, Decision.ABSTAIN.value)
        self.assertEqual(
            response.reason_codes,
            ("CONFIDENCE_THRESHOLDS_MISSING",),
        )

    def test_review_range_requires_human_approval(self):
        response = evaluate_request(
            self.request(confidence=0.70),
            self.policy,
            self.registry,
        )
        self.assertEqual(
            response.decision,
            Decision.REQUIRE_HUMAN_APPROVAL.value,
        )
        self.assertIn("CONFIDENCE_REVIEW_REQUIRED", response.reason_codes)

    def test_valid_diagnosis_is_allowed(self):
        response = evaluate_request(
            self.request(),
            self.policy,
            self.registry,
        )
        self.assertEqual(response.decision, Decision.ALLOW_DIAGNOSIS.value)
        self.assertEqual(
            response.granted_authority,
            Authority.L1_DIAGNOSE.value,
        )

    def test_recommendation_remains_recommendation_only(self):
        response = evaluate_request(
            self.request(
                requested_authority=Authority.L2_RECOMMEND.value
            ),
            self.policy,
            self.registry,
        )
        self.assertEqual(response.decision, Decision.RECOMMEND_ONLY.value)

    def test_study2_authority_is_capped_at_l2(self):
        response = evaluate_request(
            self.request(
                study_id="study_02_independent",
                data_origin="STUDY_02",
                requested_authority=Authority.L3_APPROVAL_REQUIRED.value,
            ),
            self.policy,
            self.registry,
        )
        self.assertEqual(response.decision, Decision.RECOMMEND_ONLY.value)
        self.assertEqual(
            response.granted_authority,
            Authority.L2_RECOMMEND.value,
        )
        self.assertIn("AUTHORITY_CAPPED", response.reason_codes)

    def test_study2_does_not_fall_back_to_study1_thresholds(self):
        self.policy["study_policies"]["study_02_independent"][
            "confidence_thresholds"
        ] = None

        response = evaluate_request(
            self.request(
                study_id="study_02_independent",
                data_origin="STUDY_02",
            ),
            self.policy,
            self.registry,
        )

        self.assertEqual(response.decision, Decision.ABSTAIN.value)
        self.assertEqual(
            response.reason_codes,
            ("CONFIDENCE_THRESHOLDS_MISSING",),
        )

    def test_same_input_produces_same_response(self):
        request = self.request()

        first = evaluate_request(request, self.policy, self.registry)
        second = evaluate_request(
            replace(request),
            self.policy,
            self.registry,
        )

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()