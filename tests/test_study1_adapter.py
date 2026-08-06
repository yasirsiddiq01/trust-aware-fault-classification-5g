import csv
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

from gate5g.study1_adapter import (
    DATA_ORIGIN,
    EXPECTED_COLUMNS,
    EXPECTED_FILE_COUNT,
    EXPECTED_RECORD_COUNT,
    STUDY_ID,
    Study1AdapterError,
    _read_accepted_file,
    load_study1_records,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _valid_row():
    return {
        column: "1"
        for column in EXPECTED_COLUMNS
    }


def _write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


class Study1AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_study1_records(REPO_ROOT)

    def test_loads_documented_accepted_inventory(self):
        self.assertEqual(
            len(self.records),
            EXPECTED_RECORD_COUNT,
        )

        source_files = {
            record.evidence_reference.split("#data-row=", 1)[0]
            for record in self.records
        }

        self.assertEqual(
            len(source_files),
            EXPECTED_FILE_COUNT,
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

    def test_first_record_preserves_source_values(self):
        first = self.records[0]

        self.assertEqual(
            first.evidence_reference,
            (
                "data/study_01_published/raw/accepted/"
                "trust_step1_step3_dataset_none_s0_seed1_run1.csv"
                "#data-row=1"
            ),
        )

        values = first.as_dict()

        self.assertEqual(tuple(values), EXPECTED_COLUMNS)
        self.assertEqual(values["run_id"], "1")
        self.assertEqual(values["seed"], "1")
        self.assertEqual(values["fault_type"], "none")
        self.assertEqual(values["flow_id"], "1")
        self.assertEqual(values["throughput_mbps"], "10.236785")

    def test_quarantine_is_never_loaded(self):
        self.assertTrue(
            all(
                "raw/quarantine" not in record.evidence_reference
                for record in self.records
            )
        )

    def test_record_is_immutable_and_as_dict_returns_copy(self):
        record = self.records[0]

        with self.assertRaises(FrozenInstanceError):
            record.row_number = 99

        copied_values = record.as_dict()
        copied_values["run_id"] = "changed"

        self.assertEqual(record.as_dict()["run_id"], "1")

    def test_rejects_unexpected_schema(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            csv_path = root / "wrong_schema.csv"
            columns = EXPECTED_COLUMNS[:-1]
            row = {
                column: "1"
                for column in columns
            }

            _write_csv(csv_path, columns, [row, row])

            with self.assertRaisesRegex(
                Study1AdapterError,
                "Unexpected Study 1 schema",
            ):
                _read_accepted_file(csv_path, root)

    def test_rejects_unexpected_row_count(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            csv_path = root / "wrong_rows.csv"

            _write_csv(
                csv_path,
                EXPECTED_COLUMNS,
                [_valid_row()],
            )

            with self.assertRaisesRegex(
                Study1AdapterError,
                "Expected 2 records",
            ):
                _read_accepted_file(csv_path, root)

    def test_rejects_blank_values(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            csv_path = root / "blank_value.csv"
            first_row = _valid_row()
            second_row = _valid_row()
            second_row["throughput_mbps"] = ""

            _write_csv(
                csv_path,
                EXPECTED_COLUMNS,
                [first_row, second_row],
            )

            with self.assertRaisesRegex(
                Study1AdapterError,
                "Blank Study 1 value",
            ):
                _read_accepted_file(csv_path, root)


if __name__ == "__main__":
    unittest.main()