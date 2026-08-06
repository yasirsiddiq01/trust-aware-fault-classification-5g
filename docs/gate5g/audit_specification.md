# Audit Specification

Each governed decision must create an append-only audit event.

## Required fields

- Audit event identifier
- Previous event hash
- Event hash
- Timestamp
- Request identifier
- Study identifier
- Dataset identifier or evidence reference
- Model identifier and version
- Policy version
- Prediction and confidence
- Governance decision
- Reason codes
- Requested and granted authority
- Human approval status
- Final action status

## Hash chain

The event hash is calculated from:

1. The previous event hash
2. A deterministic canonical representation of the current event

SHA-256 is used for the hash.

## Restrictions

Raw study data must not be duplicated in the audit log. Audit events contain identifiers, evidence references, policy results, and accountability information.

If a required audit event cannot be created, an operational decision must not proceed.