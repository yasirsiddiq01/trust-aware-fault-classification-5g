# Study 1 Archived Results

## Model-Level Results

| Model | Accuracy | Macro-F1 |
|---|---:|---:|
| Logistic Regression baseline | 0.642857 | 0.576720 |
| Random Forest first clean run | 0.846939 | 0.653251 |
| Balanced Random Forest | 0.704082 | 0.654652 |
| Minimal MLP | 0.857143 | 0.618072 |

The Random Forest result is described in the notebook as the **first clean
run**. It should not be labelled a tuned Random Forest unless separate tuning
evidence is recovered.

## Normal-Operation Failure

Aggregate accuracy concealed severe failure on normal-operation records.

### Random Forest first clean run

- normal-operation test records: 14;
- correctly classified as normal: 1;
- classified as radio degradation: 13;
- normal-operation recall: 0.071429.

### Minimal MLP

- normal-operation test records: 14;
- correctly classified as normal: 0;
- classified as radio degradation: 13;
- classified as traffic overload: 1;
- normal-operation recall: 0.0.

## Balanced Random Forest: Radio Severity Accuracy

| Radio severity | Correct | Total | Accuracy |
|---:|---:|---:|---:|
| 1 | 3 | 14 | 0.214286 |
| 2 | 4 | 14 | 0.285714 |
| 3 | 7 | 14 | 0.500000 |

## Interpretation Boundary

These values are historical outputs preserved in the archived notebook. They
should not yet be described as independently reproduced results because the
repository does not currently contain a verified frozen simulator and Python
environment capable of recreating the complete pipeline.
