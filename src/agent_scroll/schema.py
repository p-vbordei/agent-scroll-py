"""Schema types and lightweight runtime validation for agent-scroll."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal, TypedDict

_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_ROLES = {"user", "assistant", "tool", "system"}
_TOOL_STATUS = {"ok", "error"}


class Sig(TypedDict):
    alg: Literal["ed25519"]
    pubkey: str
    sig: str


class Turn(TypedDict, total=False):
    version: Literal["scroll/0.1"]
    turn: int
    role: str
    model: dict
    params: dict
    messages: list[dict]
    tool_calls: list[dict]
    tool_results: list[dict]
    timestamp_ns: int
    prev_hash: str


class SealedTurn(Turn, total=False):
    hash: str
    sig: Sig


@dataclass
class VerifyFailure:
    turn: int
    reason: str  # "BadHash" | "BrokenChain" | "BadSignature" | "SchemaViolation"
    detail: str | None = None


@dataclass
class VerifyResult:
    ok: bool
    failures: list[VerifyFailure]


def _check_message(m: Any) -> str | None:
    if not isinstance(m, dict):
        return "message not object"
    if not isinstance(m.get("role"), str):
        return "message.role must be string"
    c = m.get("content")
    if not (isinstance(c, str) or isinstance(c, list)):
        return "message.content must be string or array"
    return None


def _check_hash(s: Any) -> bool:
    return isinstance(s, str) and bool(_HASH_RE.match(s))


def validate_turn(value: Any) -> tuple[bool, str | None]:
    if not isinstance(value, dict):
        return False, "not an object"
    if value.get("version") != "scroll/0.1":
        return False, 'version must be "scroll/0.1"'
    if not isinstance(value.get("turn"), int) or value["turn"] < 0:
        return False, "turn must be non-negative integer"
    if value.get("role") not in _ROLES:
        return False, f"role must be one of {sorted(_ROLES)}"
    model = value.get("model")
    if not isinstance(model, dict) or not model.get("vendor") or not model.get("id"):
        return False, "model.vendor and model.id required"
    params = value.get("params")
    if not isinstance(params, dict):
        return False, "params required"
    for k in ("temperature", "top_p"):
        if not isinstance(params.get(k), (int, float)):
            return False, f"params.{k} must be number"
    for k in ("seed", "max_tokens"):
        if k in params and (not isinstance(params[k], int)):
            return False, f"params.{k} must be integer"
    msgs = value.get("messages")
    if not isinstance(msgs, list):
        return False, "messages must be array"
    for m in msgs:
        err = _check_message(m)
        if err:
            return False, err
    for k in ("tool_calls", "tool_results"):
        if k in value:
            if not isinstance(value[k], list):
                return False, f"{k} must be array"
            for tc in value[k]:
                if not isinstance(tc, dict):
                    return False, f"{k} item not object"
                if not isinstance(tc.get("id"), str):
                    return False, f"{k}.id must be string"
                if k == "tool_calls":
                    if not isinstance(tc.get("name"), str):
                        return False, "tool_calls.name must be string"
                    if not _check_hash(tc.get("args_hash")):
                        return False, "tool_calls.args_hash invalid"
                else:
                    if tc.get("status") not in _TOOL_STATUS:
                        return False, "tool_results.status must be ok|error"
                    if not _check_hash(tc.get("response_hash")):
                        return False, "tool_results.response_hash invalid"
    if not isinstance(value.get("timestamp_ns"), int) or value["timestamp_ns"] < 0:
        return False, "timestamp_ns must be non-negative integer"
    if "prev_hash" in value and not _check_hash(value["prev_hash"]):
        return False, "prev_hash invalid"
    return True, None


def validate_sealed_turn(value: Any) -> tuple[bool, str | None]:
    ok, err = validate_turn(value)
    if not ok:
        return False, err
    if not _check_hash(value.get("hash")):
        return False, "hash invalid"
    sig = value.get("sig")
    if sig is not None:
        if not isinstance(sig, dict):
            return False, "sig not object"
        if sig.get("alg") != "ed25519":
            return False, 'sig.alg must be "ed25519"'
        if not isinstance(sig.get("pubkey"), str) or not isinstance(sig.get("sig"), str):
            return False, "sig.pubkey and sig.sig required"
    return True, None
