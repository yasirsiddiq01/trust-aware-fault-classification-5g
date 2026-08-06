# GATE-5G Governance Specification

## Purpose

GATE-5G governs the operational use of AI-generated 5G fault diagnoses. It does not replace the classifier or alter original experimental evidence.

## Decisions

The policy engine returns one decision:

- `ALLOW_DIAGNOSIS`
- `RECOMMEND_ONLY`
- `REQUIRE_HUMAN_APPROVAL`
- `ABSTAIN`
- `BLOCK`

## Authority levels

- `L0_OBSERVE`: validate, record, and audit.
- `L1_DIAGNOSE`: expose a governed diagnosis.
- `L2_RECOMMEND`: recommend an action without execution.
- `L3_APPROVAL_REQUIRED`: prepare an action requiring explicit human approval.

Autonomous execution is outside the current scope.

## Control order

1. Identity and provenance
2. Input validity
3. Evidence and distribution status
4. Confidence and calibration
5. Authority enforcement
6. Audit availability

Mandatory control failures are handled through `BLOCK` or `ABSTAIN`. Missing thresholds must not be replaced with invented values.

## Study-specific limits

Study 1 supports retrospective end-to-end governance evaluation with a maximum authority of `L3_APPROVAL_REQUIRED`.

Study 2 supports partial governance integration with a maximum authority of `L2_RECOMMEND` until its independent evidence, modelling, and calibration are complete.