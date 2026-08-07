"""Read-only adapter for the verified partial Study 2 evidence."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple


STUDY_ID = "study_02_independent"
DATA_ORIGIN = "STUDY_02"

DATA_RELATIVE_PATH = (
    Path("data")
    / "study_02_independent"
    / "controlled100_s3minus16_nometa_dropunknownip_v1_merged.csv"
)

EXPECTED_SHA256 = (
    "a325d9832ae2352b3183ff2d0a1d8f224b1d9c35a161e3199b488e5adc467f34"
)

EXPECTED_RECORD_COUNT = 1400
EXPECTED_SOURCE_FILE_COUNT = 700
EXPECTED_ROWS_PER_SOURCE_FILE = 2

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
    "undelivered_packets",
    "tx_bytes",
    "rx_bytes",
    "throughput_mbps",
    "mean_delay_ms",
    "mean_jitter_ms",
    "packet_loss_ratio",
    "undelivered_ratio",
    "time_first_tx_s",
    "time_last_rx_s",
    "flow_duration_s",
    "sim_time_s",
    "source_file",
)

EXPECTED_SCENARIOS = {
    "none": ("none", "0", "0"),
    "radio_degradation_s1": ("radio_degradation", "1", "1"),
    "radio_degradation_s2": ("radio_degradation", "2", "1"),
    "radio_degradation_s3": ("radio_degradation", "3", "1"),
    "traffic_overload_s1": ("traffic_overload", "1", "1"),
    "traffic_overload_s2": ("traffic_overload", "2", "1"),
    "traffic_overload_s3": ("traffic_overload", "3", "1"),
}

EXPECTED_SCENARIO_COUNT = 200


class Study2AdapterError(RuntimeError):
    """Raised when verified Study 2 evidence violates the adapter contract."""


@dataclass(frozen=True)
class Study2EvidenceRecord:
    """One immutable flow-level record from independent Study 2 evidence."""

    evidence_reference: str
    row_number: int
    values: Tuple[Tuple[str, str], ...]
    study_id: str = STUDY_ID
    data_origin: str = DATA_ORIGIN

    def as_dict(self) -> Dict[str, str]:
        """Return a mutable copy without altering the preserved record."""

        return dict(self.values)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as evidence_file:
        for chunk in iter(lambda: evidence_file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def _validate_rows(rows: Tuple[Dict[str, str], ...]) -> None:
    if len(rows) != EXPECTED_RECORD_COUNT:
        raise Study2AdapterError(
            f"Expected {EXPECTED_RECORD_COUNT} Study 2 records; "
            f"found {len(rows)}."
        )

    row_values = []

    for row_number, row in enumerate(rows, start=1):
        if None in row:
            raise Study2AdapterError(
                f"Unexpected additional values in Study 2 data row "
                f"{row_number}."
            )

        if any(
            row.get(column) is None or row[column] == ""
            for column in EXPECTED_COLUMNS
        ):
            raise Study2AdapterError(
                f"Blank Study 2 value in data row {row_number}."
            )

        scenario = row["scenario_id"]
        expected = EXPECTED_SCENARIOS.get(scenario)

        if expected is None:
            raise Study2AdapterError(
                f"Unexpected Study 2 scenario_id in data row "
                f"{row_number}: {scenario}"
            )

        expected_fault_type, expected_severity, expected_active = expected

        if (
            row["fault_type"] != expected_fault_type
            or row["fault_severity"] != expected_severity
            or row["fault_active"] != expected_active
        ):
            raise Study2AdapterError(
                f"Inconsistent Study 2 scenario metadata in data row "
                f"{row_number}."
            )

        row_values.append(
            tuple(row[column] for column in EXPECTED_COLUMNS)
        )

    if len(set(row_values)) != len(row_values):
        raise Study2AdapterError(
            "Exact duplicate Study 2 records detected."
        )

    scenario_counts = Counter(
        row["scenario_id"]
        for row in rows
    )

    expected_scenario_counts = {
        scenario: EXPECTED_SCENARIO_COUNT
        for scenario in EXPECTED_SCENARIOS
    }

    if scenario_counts != expected_scenario_counts:
        raise Study2AdapterError(
            "Unexpected Study 2 scenario distribution."
        )

    source_counts = Counter(
        row["source_file"]
        for row in rows
    )

    if len(source_counts) != EXPECTED_SOURCE_FILE_COUNT:
        raise Study2AdapterError(
            f"Expected {EXPECTED_SOURCE_FILE_COUNT} Study 2 source files; "
            f"found {len(source_counts)}."
        )

    if any(
        count != EXPECTED_ROWS_PER_SOURCE_FILE
        for count in source_counts.values()
    ):
        raise Study2AdapterError(
            "Each Study 2 source file must contribute exactly "
            f"{EXPECTED_ROWS_PER_SOURCE_FILE} records."
        )

    runs = {
        row["run_id"]
        for row in rows
    }

    expected_runs = {
        str(run)
        for run in range(1, 101)
    }

    if runs != expected_runs:
        raise Study2AdapterError(
            "Study 2 run_id values must be exactly 1 through 100."
        )

    flows = {
        row["flow_id"]
        for row in rows
    }

    if flows != {"1", "2"}:
        raise Study2AdapterError(
            "Study 2 flow_id values must be exactly 1 and 2."
        )


def load_study2_records(
    repo_root: Path,
) -> Tuple[Study2EvidenceRecord, ...]:
    """Load only the verified independent Study 2 merged evidence."""

    root = Path(repo_root).resolve()
    csv_path = root / DATA_RELATIVE_PATH

    if not csv_path.is_file():
        raise Study2AdapterError(
            f"Study 2 evidence file is missing: {DATA_RELATIVE_PATH.as_posix()}"
        )

    try:
        relative_path = csv_path.resolve().relative_to(root).as_posix()
    except ValueError as exc:
        raise Study2AdapterError(
            "Study 2 evidence file is outside the repository."
        ) from exc

    actual_sha256 = _sha256(csv_path)

    if actual_sha256 != EXPECTED_SHA256:
        raise Study2AdapterError(
            "Study 2 evidence SHA-256 does not match the verified artifact."
        )

    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        actual_columns = tuple(reader.fieldnames or ())

        if actual_columns != EXPECTED_COLUMNS:
            raise Study2AdapterError(
                "Unexpected Study 2 schema."
            )

        rows = tuple(reader)

    _validate_rows(rows)

    return tuple(
        Study2EvidenceRecord(
            evidence_reference=(
                f"{relative_path}#data-row={row_number}"
            ),
            row_number=row_number,
            values=tuple(
                (column, row[column])
                for column in EXPECTED_COLUMNS
            ),
        )
        for row_number, row in enumerate(rows, start=1)
    )
