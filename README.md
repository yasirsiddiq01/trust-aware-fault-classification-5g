# Trust-Aware Fault Classification in 5G Networks (ns-3 / 5G-LENA)

## Overview

This repository contains the implementation and experimental pipeline for trust-aware fault classification in 5G networks using QoS-derived features. The study is based on ns-3 (5G-LENA) simulations and evaluates the limitations of QoS observability under varying network fault conditions.

## Problem Statement

Reliable fault detection in 5G networks is challenging due to limited observability at the QoS level. Subtle network degradations often exhibit overlapping feature representations, making classification unstable and unreliable. This work investigates the impact of feature-space limitations on fault detectability.

## Contributions

* Leakage-safe grouped evaluation protocol for QoS-based classification
* Feature engineering for enhanced observability (packet_loss_ratio, jitter_delay_ratio, interaction terms)
* Comparative analysis of Logistic Regression and Random Forest models
* Trust-aware evaluation using confidence and margin analysis
* ns-3 (5G-LENA) simulation pipeline for controlled fault injection

## Repository Structure

* `ns3_simulation/` – Simulation scripts and scenario definitions
* `data/` – Raw and processed datasets
* `src/` – ML pipeline (preprocessing, models, evaluation)
* `experiments/` – Reproducible experiment configurations
* `results/` – Output figures and logs
* `paper/` – Manuscript and figures

## Dataset

The dataset is generated using ns-3 5G-LENA simulations with the following fault scenarios:

* `none` (normal operation)
* `radio_degradation`
* `traffic_overload`

QoS Features:

* Throughput
* Delay
* Jitter
* Packet loss
* Engineered features (ratios and interactions)

## Methodology

### 1. Simulation

* 5G-LENA ns-3 environment
* Urban Micro (UMi) propagation model
* Controlled fault injection (radio + traffic)

### 2. Feature Engineering

* QoS extraction
* Derived features for better separability
* Group-aware splitting to prevent leakage

### 3. Modeling

* Logistic Regression (baseline + balanced)
* Random Forest (standard + balanced)

### 4. Evaluation

* Accuracy
* Macro F1-score
* Confusion matrix
* Confidence and margin analysis

## Installation

```bash
git clone https://github.com/yasirsiddiq01/trust-aware-fault-classification-5g.git
cd trust-aware-fault-classification-5g
pip install -r requirements.txt
```

## Running Experiments

```bash
python src/main.py --config config/rf.yaml
```

## Reproducibility

All experiments are controlled via configuration files in the `config/` directory. Each experiment folder contains logs and outputs to ensure full reproducibility.

## Results

Key findings:

* QoS-based features struggle with subtle radio degradations
* Structural overlap leads to unstable classification boundaries
* Balanced models improve recall but not feature separability

## Limitations

* Limited feature observability at QoS level
* No PHY-layer information included
* Simulation-based evaluation (no real-world traces)

## Future Work

* Integration of PHY/MAC-level telemetry
* Uncertainty-aware models
* Agentic fault diagnosis using LLM-based reasoning

## Paper

Title: *A Leakage-Safe Study of Trust-Aware Fault Classification in ns-3/5G-LENA Using QoS-Derived Features*

(Will be updated after publication)

## Citation

If you use this work, please cite:

```bibtex
@article{paper2026,
  title={Trust-Aware Fault Classification in 5G Networks},
  author={Yasir Siddiq},
  year={2026}
}
```

## License

MIT License

## Contact

For questions or collaboration:
mailto: yasir.sre@gmail.com
