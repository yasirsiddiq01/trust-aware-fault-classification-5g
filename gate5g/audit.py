"""Tamper-evident audit hashing for GATE-5G."""

import hashlib
import json
from typing import Any, Dict, Iterable

GENESIS_HASH = "0" * 64
_RESERVED_FIELDS = {"event_hash", "previous_event_hash"}


def canonical_json(value: Dict[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def append_audit_event(
    payload: Dict[str, Any],
    previous_event_hash: str = GENESIS_HASH,
) -> Dict[str, Any]:
    if _RESERVED_FIELDS.intersection(payload):
        raise ValueError("Audit payload contains reserved fields.")

    event = dict(payload)
    event["previous_event_hash"] = previous_event_hash

    digest = hashlib.sha256(
        canonical_json(event).encode("utf-8")
    ).hexdigest()

    event["event_hash"] = digest
    return event


def verify_audit_chain(events: Iterable[Dict[str, Any]]) -> bool:
    expected_previous_hash = GENESIS_HASH

    for event in events:
        if event.get("previous_event_hash") != expected_previous_hash:
            return False

        event_hash = event.get("event_hash")

        if not isinstance(event_hash, str):
            return False

        event_without_hash = {
            key: value
            for key, value in event.items()
            if key != "event_hash"
        }

        calculated_hash = hashlib.sha256(
            canonical_json(event_without_hash).encode("utf-8")
        ).hexdigest()

        if calculated_hash != event_hash:
            return False

        expected_previous_hash = event_hash

    return True