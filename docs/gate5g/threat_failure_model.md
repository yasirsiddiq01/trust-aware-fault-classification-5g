# Threat and Failure Model

GATE-5G must address the following failure classes:

## Evidence failures

- Missing provenance
- Incorrect dataset identity
- Study mismatch
- Mixed-study input
- Unregistered evidence
- Incomplete evidence presented as complete

## Model-output failures

- Missing prediction
- Missing confidence
- Invalid probability values
- Unsupported class
- Unknown model version
- Missing calibration
- Out-of-distribution input

## Governance failures

- Unknown policy version
- Authority request above the permitted level
- Human approval bypass
- Non-deterministic policy result
- Audit write failure
- Audit-chain tampering

## Required response

Identity, provenance, schema, model-registration, policy-registration, and audit failures must fail closed.

Uncertainty, incomplete calibration, unsupported classes, and distribution shift must result in abstention unless a stricter block is required.