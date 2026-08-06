"""Read-only adapter for the validated Study 1 evidence package."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple


STUDY_ID = "study_01_published"
DATA_ORIGIN = "STUDY_01"

ACCEPTED_RELATIVE_PATH = (
    Path("data")
    / "study_01_published"
    / "raw"
    / "accepted"
)

EXPECTED_FILE_COUNT = 231
EXPECTED_RECORD_COUNT = 462
EXPECTED_ROWS_PER_FILE = 2

EXPECTED_COLUMNS: Tuple[str, ...] = (
    "run_id",
    "seed",
    "scenario_id",
    "fault_type",
    "fault_active",
    "fault_severity",
    "gNb_num",
    "ue_per_gNb",
    "effective_lambda_ull",
    "effective_lambda_be",
    "flow_id",
    "src_ip",
    "dst_ip",
    "protocol",
    "src_port",
    "dst_port",
    "tx_packets",
    "rx_packets",
    "lost_packets",
    "tx_bytes",
    "rx_bytes",
    "throughput_mbps",
    "mean_delay_ms",
    "mean_jitter_ms",
    "packet_loss_ratio",
    "time_first_tx_s",
    "time_last_rx_s",
    "flow_duration_s",
    "sim_time_s",
)


class Study1AdapterError(RuntimeError):
    """Raised when frozen Study 1 evidence violates the adapter contract."""


@dataclass(frozen=True)
class Study1EvidenceRecord:
    """One immutable flow-level record from accepted Study 1 evidence."""

    evidence_reference: str
    row_number: int
    values: Tuple[Tuple[str, str], ...]
    study_id: str = STUDY_ID
    data_origin: str = DATA_ORIGIN

    def as_dict(self) -> Dict[str, str]:
        """Return a mutable copy without altering the preserved record."""

        return dict(self.values)


def _read_accepted_file(
    csv_path: Path,
    repo_root: Path,
) -> Tuple[Study1EvidenceRecord, ...]:
    path = Path(csv_path)
    root = Path(repo_root).resolve()

    if not path.is_file():
        raise Study1AdapterError(
            f"Accepted Study 1 evidence file is missing: {path}"
        )

    try:
        relative_path = path.resolve().relative_to(root).as_posix()
    except ValueError as exc:
        raise Study1AdapterError(
            "Study 1 evidence file is outside the repository."
        ) from exc

    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        actual_columns = tuple(reader.fieldnames or ())

        if actual_columns != EXPECTED_COLUMNS:
            raise Study1AdapterError(
                f"Unexpected Study 1 schema in {relative_path}."
            )

        rows = list(reader)

    if len(rows) != EXPECTED_ROWS_PER_FILE:
        raise Study1AdapterError(
            f"Expected {EXPECTED_ROWS_PER_FILE} records in "
            f"{relative_path}; found {len(rows)}."
        )

    records = []

    for row_number, row in enumerate(rows, start=1):
        if None in row:
            raise Study1AdapterError(
                f"Unexpected additional values in {relative_path}, "
                f"data row {row_number}."
            )

        if any(
            row.get(column) is None or row[column] == ""
            for column in EXPECTED_COLUMNS
        ):
            raise Study1AdapterError(
                f"Blank Study 1 value in {relative_path}, "
                f"data row {row_number}."
            )

        values = tuple(
            (column, row[column])
            for column in EXPECTED_COLUMNS
        )

        records.append(
            Study1EvidenceRecord(
                evidence_reference=(
                    f"{relative_path}#data-row={row_number}"
                ),
                row_number=row_number,
                values=values,
            )
        )

    return tuple(records)


def load_study1_records(
    repo_root: Path,
) -> Tuple[Study1EvidenceRecord, ...]:
    """Load only frozen accepted Study 1 records in deterministic order."""

    root = Path(repo_root).resolve()
    accepted_directory = root / ACCEPTED_RELATIVE_PATH

    if not accepted_directory.is_dir():
        raise Study1AdapterError(
            "Accepted Study 1 evidence directory is missing."
        )

    csv_files = tuple(
        sorted(
            (
                path
                for path in accepted_directory.iterdir()
                if path.is_file() and path.suffix.lower() == ".csv"
            ),
            key=lambda path: path.name,
        )
    )

    if len(csv_files) != EXPECTED_FILE_COUNT:
        raise Study1AdapterError(
            f"Expected {EXPECTED_FILE_COUNT} accepted Study 1 CSV files; "
            f"found {len(csv_files)}."
        )

    records = []

    for csv_path in csv_files:
        records.extend(_read_accepted_file(csv_path, root))

    if len(records) != EXPECTED_RECORD_COUNT:
        raise Study1AdapterError(
            f"Expected {EXPECTED_RECORD_COUNT} accepted Study 1 records; "
            f"found {len(records)}."
        )

    return tuple(records)