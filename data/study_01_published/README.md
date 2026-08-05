# Study 1 Dataset

## Directory Contents

```text
raw/accepted/
    231 accepted simulation CSV files

raw/quarantine/
    12 CSV files from two incomplete simulation blocks

manifests/
    DATASET_STATE_STEP3_CAMPAIGN_V1.txt
    excluded_blocks_step3_campaign_v1.csv
    archive_sha256.txt
    notebook_sha256.txt
    dataset_inventory.csv
```

## Accepted Dataset

The accepted raw data contains 33 complete `seed + run_id` groups, seven
fault/severity conditions per group, two flow rows per condition, fourteen rows
per group, 462 rows in total, and 29 columns.

## Quarantine Policy

Incomplete simulation blocks were excluded as complete groups. The quarantine
directory preserves the six successful conditions from each failed block.
These records must not be mixed with the accepted dataset when performing the
published Study 1 evaluation.

## Integrity Records

`dataset_inventory.csv` records repository-relative file path, file size, and
SHA-256 checksum.

The original compressed archive is preserved at:
`archive/study_01_published/step3_campaign_v1_bundle.tar.gz`.

## Data Use Warning

The CSV records are simulation outputs. They are not production network data
and must not be presented as real operator telemetry.
