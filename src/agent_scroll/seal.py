"""seal() and seal_chain() — hash and optionally sign turns."""

from __future__ import annotations

import base64
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .canonical import canonical, hash_canonical
from .schema import SealedTurn, Turn


@dataclass
class SignOpts:
    privkey: bytes  # 32 bytes raw Ed25519 seed
    pubkey: bytes  # 32 bytes raw Ed25519 pubkey


def seal(turn: Turn, sign: SignOpts | None = None) -> SealedTurn:
    h = hash_canonical(turn)
    if sign is None:
        return {**turn, "hash": h}
    sk = Ed25519PrivateKey.from_private_bytes(sign.privkey)
    sig_bytes = sk.sign(canonical(turn))
    return {
        **turn,
        "hash": h,
        "sig": {
            "alg": "ed25519",
            "pubkey": base64.b64encode(sign.pubkey).decode("ascii"),
            "sig": base64.b64encode(sig_bytes).decode("ascii"),
        },
    }


def seal_chain(turns: list[Turn], sign: SignOpts | None = None) -> list[SealedTurn]:
    out: list[SealedTurn] = []
    prev: str | None = None
    for t in turns:
        linked = dict(t)
        if prev is not None and "prev_hash" not in linked:
            linked["prev_hash"] = prev
        sealed = seal(linked, sign)
        out.append(sealed)
        prev = sealed["hash"]
    return out
