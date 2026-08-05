# Study 1 Methodology

## Unit of Analysis

The raw records are flow-level observations. The independent experimental unit
is the simulation block identified by `seed + run_id`.

Both flows from every condition within the same block must remain in the same
model partition.

## Dataset Integrity

The accepted package contains:

- 33 complete block groups;
- 14 records per group;
- 7 unique conditions per group;
- 2 flows per condition;
- 462 accepted records;
- no blank accepted values;
- no exact duplicated accepted records;
- one consistent 29-column schema.

## Original Columns

The accepted CSV schema contains:

1. `run_id`
2. `seed`
3. `scenario_id`
4. `fault_type`
5. `fault_active`
6. `fault_severity`
7. `gNb_num`
8. `ue_per_gNb`
9. `effective_lambda_ull`
10. `effective_lambda_be`
11. `flow_id`
12. `src_ip`
13. `dst_ip`
14. `protocol`
15. `src_port`
16. `dst_port`
17. `tx_packets`
18. `rx_packets`
19. `lost_packets`
20. `tx_bytes`
21. `rx_bytes`
22. `throughput_mbps`
23. `mean_delay_ms`
24. `mean_jitter_ms`
25. `packet_loss_ratio`
26. `time_first_tx_s`
27. `time_last_rx_s`
28. `flow_duration_s`
29. `sim_time_s`

## Exclusion Rule

A simulation block was retained only when all seven expected conditions were
available.

| Seed | Run | Reason |
|---:|---:|---|
| 3 | 3 | `radio_degradation_s3_crash` |
| 7 | 2 | `radio_degradation_s3_crash` |

Their remaining six conditions were preserved in quarantine rather than mixed
with the complete dataset.

## Group-Safe Split

The archived notebook records:

- 26 training groups;
- 7 test groups;
- 364 training rows;
- 98 test rows;
- zero group overlap;
- random state 42.

The archived test groups were:

```text
2_run4
2_run5
4_run2
4_run4
5_run1
6_run3
7_run4
```

## Feature Engineering

The archived notebook created derived features including:

- `packet_loss_ratio`;
- `throughput_efficiency`;
- `jitter_delay_ratio`;
- `loss_delay_interaction`;
- `loss_jitter_interaction`.

The refined analysis dataset was recorded as
`step3_ml_ready_fault_type_augmented_v3_refined.csv`.

The current repository preserves the original simulation CSV files and the
analysis notebook. Derived datasets will be added only after their provenance
and generation steps are verified.
