"""verify(chain, pubkey?) — check hash, chain links, and (optionally) signatures."""

from __future__ import annotations

import base64
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .canonical import canonical, hash_canonical
from .schema import VerifyFailure, VerifyResult, validate_sealed_turn


def verify(chain: list[Any], pubkey: bytes | None = None) -> VerifyResult:
    failures: list[VerifyFailure] = []
    prev_hash: str | None = None

    for i, item in enumerate(chain):
        ok, err = validate_sealed_turn(item)
        if not ok:
            failures.append(VerifyFailure(turn=i, reason="SchemaViolation", detail=err))
            prev_hash = None
            continue

        sealed: dict = item
        h = sealed["hash"]
        sig = sealed.get("sig")
        turn_only = {k: v for k, v in sealed.items() if k not in ("hash", "sig")}

        if hash_canonical(turn_only) != h:
            failures.append(VerifyFailure(turn=i, reason="BadHash"))
            prev_hash = h
            continue

        if i > 0 and turn_only.get("prev_hash") != prev_hash:
            failures.append(VerifyFailure(turn=i, reason="BrokenChain"))

        if sig is not None and pubkey is not None:
            try:
                sig_bytes = base64.b64decode(sig["sig"])
                pk = Ed25519PublicKey.from_public_bytes(pubkey)
                pk.verify(sig_bytes, canonical(turn_only))
            except (InvalidSignature, ValueError, Exception):
                failures.append(VerifyFailure(turn=i, reason="BadSignature"))

        prev_hash = h

    return VerifyResult(ok=(len(failures) == 0), failures=failures)
