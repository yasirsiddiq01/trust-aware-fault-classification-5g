import unittest

from gate5g.audit import (
    append_audit_event,
    canonical_json,
    verify_audit_chain,
)


class AuditTests(unittest.TestCase):
    def test_canonical_json_is_deterministic(self):
        first = canonical_json({"b": 2, "a": 1})
        second = canonical_json({"a": 1, "b": 2})
        self.assertEqual(first, second)

    def test_valid_chain_passes(self):
        first = append_audit_event(
            {"request_id": "REQ-001", "decision": "ALLOW_DIAGNOSIS"}
        )
        second = append_audit_event(
            {"request_id": "REQ-002", "decision": "ABSTAIN"},
            first["event_hash"],
        )

        self.assertTrue(verify_audit_chain([first, second]))

    def test_modified_event_fails(self):
        event = append_audit_event(
            {"request_id": "REQ-001", "decision": "ALLOW_DIAGNOSIS"}
        )
        event["decision"] = "BLOCK"

        self.assertFalse(verify_audit_chain([event]))

    def test_broken_previous_hash_fails(self):
        first = append_audit_event(
            {"request_id": "REQ-001", "decision": "ALLOW_DIAGNOSIS"}
        )
        second = append_audit_event(
            {"request_id": "REQ-002", "decision": "ABSTAIN"},
            first["event_hash"],
        )
        second["previous_event_hash"] = "f" * 64

        self.assertFalse(verify_audit_chain([first, second]))

    def test_reserved_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            append_audit_event({"event_hash": "not-allowed"})


if __name__ == "__main__":
    unittest.main()