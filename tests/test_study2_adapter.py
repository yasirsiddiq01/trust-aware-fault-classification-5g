import tempfile
import unittest
from collections import Counter
from dataclasses import FrozenInstanceError
from pathlib import Path

from gate5g.study2_adapter import (
    DATA_ORIGIN,
    DATA_RELATIVE_PATH,
    EXPECTED_COLUMNS,
    EXPECTED_RECORD_COUNT,
    EXPECTED_SCENARIOS,
    EXPECTED_SCENARIO_COUNT,
    EXPECTED_SOURCE_FILE_COUNT,
    STUDY_ID,
    Study2AdapterError,
    load_study2_records,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class Study2AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_study2_records(REPO_ROOT)

    def test_loads_verified_independent_evidence(self):
        self.assertEqual(
            len(self.records),
            EXPECTED_RECORD_COUNT,
        )

        self.assertTrue(
            all(record.study_id == STUDY_ID for record in self.records)
        )
        self.assertTrue(
            all(
                record.data_origin == DATA_ORIGIN
                for record in self.records
            )
        )

    def test_preserves_verified_schema_and_values(self):
        first = self.records[0]
        values = first.as_dict()

        self.assertEqual(tuple(values), EXPECTED_COLUMNS)
        self.assertEqual(values["run_id"], "1")
        self.assertEqual(values["flow_id"], "1")
        self.assertEqual(values["scenario_id"], "none")
        self.assertEqual(values["fault_type"], "none")
        self.assertEqual(values["fault_severity"], "0")
        self.assertEqual(values["fault_active"], "0")

    def test_evidence_references_use_only_study2_path(self):
        expected_prefix = DATA_RELATIVE_PATH.as_posix()

        self.assertTrue(
            all(
                record.evidence_reference.startswith(
                    expected_prefix + "#data-row="
                )
                for record in self.records
            )
        )

        self.assertTrue(
            all(
                "study_01" not in record.evidence_reference
                for record in self.records
            )
        )

    def test_scenario_distribution_matches_verified_artifact(self):
        scenario_counts = Counter(
            record.as_dict()["scenario_id"]
            for record in self.records
        )

        self.assertEqual(
            scenario_counts,
            {
                scenario: EXPECTED_SCENARIO_COUNT
                for scenario in EXPECTED_SCENARIOS
            },
        )

    def test_source_file_inventory_is_independent(self):
        source_counts = Counter(
            record.as_dict()["source_file"]
            for record in self.records
        )

        self.assertEqual(
            len(source_counts),
            EXPECTED_SOURCE_FILE_COUNT,
        )

        self.assertTrue(
            all(count == 2 for count in source_counts.values())
        )

        self.assertTrue(
            all(
                "study_01" not in source_file.lower()
                and "study-01" not in source_file.lower()
                for source_file in source_counts
            )
        )

    def test_record_is_immutable_and_as_dict_returns_copy(self):
        record = self.records[0]

        with self.assertRaises(FrozenInstanceError):
            record.row_number = 99

        copied_values = record.as_dict()
        copied_values["run_id"] = "changed"

        self.assertEqual(
            record.as_dict()["run_id"],
            "1",
        )

    def test_missing_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)

            with self.assertRaisesRegex(
                Study2AdapterError,
                "Study 2 evidence file is missing",
            ):
                load_study2_records(root)

    def test_modified_evidence_fails_sha256_check(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            evidence_path = root / DATA_RELATIVE_PATH

            evidence_path.parent.mkdir(parents=True)
            evidence_path.write_text(
                "not-the-verified-study-2-evidence\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                Study2AdapterError,
                "SHA-256",
            ):
                load_study2_records(root)


if __name__ == "__main__":
    unittest.main()
