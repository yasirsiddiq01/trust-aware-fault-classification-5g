# Study 1: Published Fault-Classification Evidence

## Status

This directory documents the recovered evidence package for the first
ns-3/5G-LENA fault-classification study.

The associated paper has been published. Citation metadata is not included
until the publication record and redistribution permissions are verified.

## Experimental Design

The campaign used seven network conditions:

| Fault type | Severity |
|---|---:|
| none | 0 |
| traffic_overload | 1 |
| traffic_overload | 2 |
| traffic_overload | 3 |
| radio_degradation | 1 |
| radio_degradation | 2 |
| radio_degradation | 3 |

Each retained simulation block contains seven conditions, two recorded flows
per condition, and fourteen flow records in total.

## Campaign Outcome

| Item | Count |
|---|---:|
| Planned simulation blocks | 35 |
| Retained complete blocks | 33 |
| Excluded incomplete blocks | 2 |
| Accepted simulation CSV files | 231 |
| Accepted flow records | 462 |
| Quarantined CSV files | 12 |
| Quarantined flow records | 24 |

The excluded groups were `3_run3` and `7_run2`. Both were excluded because
`radio_degradation` severity 3 failed, leaving an incomplete condition set.

## Evidence Boundary

The archive and notebook establish the retained and quarantined data structure,
the leakage-safe grouping identifier, feature-engineering steps, historical
model metrics, and class-specific error patterns.

They do not yet establish a complete frozen simulator environment or a fully
independent rerun of the original experiment.
