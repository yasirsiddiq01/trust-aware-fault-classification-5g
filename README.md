# Trust-Aware Fault Classification in 5G Networks

This repository preserves and documents simulation evidence for trust-aware
fault classification using ns-3/5G-LENA QoS measurements.

The repository is being developed in three distinct research stages:

| Stage | Scope | Current repository status |
|---|---|---|
| Study 1 | Initial seven-condition fault-classification experiment | Evidence package recovered and under repository review |
| Study 2 | Expanded 700-simulation campaign with refined radio severities | Not yet added to this repository |
| GATE-5G | Governance and assurance extension for AI-assisted incident response | Planned; not yet implemented |

## Current Scope

The current branch contains the recovered evidence package for Study 1.

Study 1 evaluated three network-condition classes:

- normal operation;
- traffic overload;
- radio degradation.

Traffic-overload and radio-degradation conditions each contained three
severity levels.

## Study 1 Dataset

The original campaign planned 35 simulation blocks. Two blocks were excluded
because the `radio_degradation` severity-3 simulation failed, leaving
incomplete seven-condition blocks.

The retained package contains:

- 33 complete simulation blocks;
- 7 conditions per block;
- 231 accepted simulation CSV files;
- 2 flow records per condition;
- 462 accepted flow-level records;
- 29 original columns;
- 12 quarantined CSV files;
- 24 quarantined flow records;
- no blank values in accepted records;
- no exact duplicate accepted records.

The grouping unit is the combined `seed` and `run_id`. All flows from the same
simulation block must remain in the same model partition.

## Archived Model Results

| Model | Accuracy | Macro-F1 |
|---|---:|---:|
| Logistic Regression baseline | 0.642857 | 0.576720 |
| Random Forest first clean run | 0.846939 | 0.653251 |
| Balanced Random Forest | 0.704082 | 0.654652 |
| Minimal MLP | 0.857143 | 0.618072 |

These are historical outputs preserved in the archived notebook. They have not
yet been independently rerun from a fully reconstructed simulator and Python
environment in this repository.

## Why Governance Is Needed

Overall accuracy did not provide a complete account of model reliability.

The archived results show that:

- the Random Forest correctly identified only 1 of 14 normal-operation test records;
- the MLP correctly identified 0 of 14 normal-operation test records;
- high aggregate accuracy therefore coexisted with severe class-specific failure.

This motivates the future GATE-5G extension, which will study calibrated
confidence, abstention, evidence completeness, distribution-shift warnings,
human escalation, action-risk controls, authorization requirements, and
structured audit logging.

No governance engine or autonomous recovery capability is implemented in the
current Study 1 package.

## Repository Structure

```text
archive/study_01_published/
    Original compressed evidence archive

data/study_01_published/
    Accepted raw CSV files, quarantined files, and integrity manifests

notebooks/study_01_published/
    Archived analysis and feature-engineering notebook

docs/study_01_published/
    Methodology, results, limitations, and provenance documentation
```

## Reproducibility Status

The repository currently preserves:

- original accepted and quarantined CSV evidence;
- exclusion records;
- dataset-state documentation;
- file hashes;
- an evidence inventory;
- the archived analysis notebook.

The repository does not yet contain verified evidence for:

- the exact original ns-3 version;
- the exact original 5G-LENA version;
- the canonical original simulation source;
- a complete frozen Python environment;
- an independently rerun end-to-end reproduction.

The current package should therefore be described as a recovered experimental
evidence and analysis record, not yet as full end-to-end simulator reproduction.

## Documentation

- [Study 1 overview](docs/study_01_published/README.md)
- [Methodology](docs/study_01_published/methodology.md)
- [Archived results](docs/study_01_published/results.md)
- [Limitations](docs/study_01_published/limitations.md)
- [Dataset documentation](data/study_01_published/README.md)

## Publication Status

The associated Study 1 paper has been published. The verified publication
citation and permitted manuscript version will be added after publisher and
copyright details are confirmed.

## License Status

Repository-wide licensing is under review. Individual third-party source files,
if added later, will retain their original licence headers. No licence claim
should be inferred for materials that do not yet have an explicit licence.
