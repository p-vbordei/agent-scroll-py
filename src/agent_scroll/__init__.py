"""agent-scroll — byte-deterministic transcript format for AI-agent conversations."""

from .canonical import canonical, hash_canonical
from .schema import (
    SealedTurn,
    Sig,
    Turn,
    VerifyFailure,
    VerifyResult,
    validate_sealed_turn,
    validate_turn,
)
from .seal import SignOpts, seal, seal_chain
from .serialize import deserialize, serialize
from .verify import verify

__all__ = [
    "SealedTurn",
    "Sig",
    "SignOpts",
    "Turn",
    "VerifyFailure",
    "VerifyResult",
    "canonical",
    "deserialize",
    "hash_canonical",
    "seal",
    "seal_chain",
    "serialize",
    "validate_sealed_turn",
    "validate_turn",
    "verify",
]
