"""serialize/deserialize Turn or SealedTurn through canonical JSON bytes."""

from __future__ import annotations

import json
from typing import Any

from .canonical import canonical
from .schema import validate_sealed_turn, validate_turn


def serialize(value: Any) -> bytes:
    return canonical(value)


def deserialize(data: bytes) -> Any:
    parsed = json.loads(data.decode("utf-8"))
    sealed_ok, _ = validate_sealed_turn(parsed)
    if sealed_ok:
        return parsed
    turn_ok, err = validate_turn(parsed)
    if turn_ok:
        return parsed
    raise ValueError(f"deserialize: invalid Turn or SealedTurn: {err}")
