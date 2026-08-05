# Study 1 Limitations

## Simulation-Based Evidence

The dataset was generated in ns-3/5G-LENA and does not contain operational
telecom-network traces. Results must not be generalized directly to production
5G environments.

## Limited Observability

The study uses QoS and FlowMonitor-derived measurements. It does not yet provide
a complete PHY-, MAC-, RAN-, or core-network observability model. Different
faults may therefore overlap in the available feature space.

## Correlated Flow Records

The 462 rows are not 462 independent simulation experiments. They represent 33
independent retained simulation blocks, seven conditions per block, and two
correlated flows per condition. Evaluation must preserve block-level grouping.

## Small Test Group Count

The archived held-out split contains seven test groups. Class-specific
performance estimates may therefore be unstable.

## Historical Notebook Record

The notebook contains stored outputs but cleared or null execution counters. It
preserves analysis evidence but does not prove that every cell can currently
execute in sequence without rebuilding dependencies and paths.

## Absolute Colab Paths

The notebook contains standard `/content/...` paths and one generic Google
Drive placeholder:
`/content/drive/MyDrive/path/to/step3_campaign_v1_bundle.tar.gz`.

These paths contain no detected personal identifiers, but they require
adaptation when rerunning the notebook.

## Incomplete Environment Provenance

The repository does not yet verify the exact original ns-3 version, exact
5G-LENA version, compiler and build configuration, canonical simulation source,
complete Python package versions, or hardware and operating-system details.

## Governance Not Yet Implemented

The repository currently documents model reliability problems. It does not yet
implement calibration, selective prediction, abstention, distribution-shift
detection, action-risk classification, human authorization, policy enforcement,
or governance audit logging. Those controls belong to the later GATE-5G
extension.
