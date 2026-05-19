"""Mirror of TS conformance suite c1–c4."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from agent_scroll import (
    SignOpts,
    canonical,
    deserialize,
    seal_chain,
    serialize,
    verify,
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def _pub(sk: Ed25519PrivateKey) -> bytes:
    return sk.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def _gen_keypair() -> tuple[bytes, bytes]:
    sk = Ed25519PrivateKey.generate()
    priv = sk.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return priv, _pub(sk)


def test_c1_byte_equality():
    turns = json.loads((FIXTURES / "c1-turns.json").read_text(encoding="utf-8"))
    hex_map = json.loads((FIXTURES / "c1-hex.json").read_text(encoding="utf-8"))
    assert len(hex_map) >= 20, f"expected >=20 vectors, got {len(hex_map)}"
    for k, t in enumerate(turns):
        bytes_ = canonical(t)
        actual = bytes_.hex()
        expected = hex_map[str(k)]
        assert actual == expected, (
            f"C1: turn {k} mismatch\n  actual:   {actual[:80]}...\n  expected: {expected[:80]}..."
        )


def test_c2_mutation_detection():
    priv, pub = _gen_keypair()
    base = {
        "version": "scroll/0.1",
        "turn": 0,
        "role": "user",
        "model": {"vendor": "anthropic", "id": "claude-sonnet-4-5"},
        "params": {"temperature": 0, "top_p": 1},
        "messages": [{"role": "user", "content": "mutation test payload"}],
        "timestamp_ns": 1700000000000000000,
    }
    [sealed] = seal_chain([base], SignOpts(privkey=priv, pubkey=pub))
    # Part A: flip each char of hash.
    hash_hex = sealed["hash"][len("sha256:") :]
    caught = 0
    for i in range(len(hash_hex)):
        flipped = list(hash_hex)
        flipped[i] = "f" if flipped[i] == "0" else "0"
        tampered = {**sealed, "hash": f"sha256:{''.join(flipped)}"}
        r = verify([tampered], pub)
        if not r.ok:
            caught += 1
    assert caught == len(hash_hex), f"caught {caught}/{len(hash_hex)}"

    # Part B: mutate body bytes.
    turn_only = {k: v for k, v in sealed.items() if k not in ("hash", "sig")}
    body = canonical(turn_only)
    limit = min(len(body), 256)
    fails = 0
    for i in range(limit):
        mutated = bytearray(body)
        mutated[i] ^= 0x80
        try:
            text = mutated.decode("utf-8")
            parsed = json.loads(text)
        except Exception:
            fails += 1
            continue
        chain = [{**parsed, "hash": sealed["hash"], "sig": sealed.get("sig")}]
        try:
            r = verify(chain, pub)
            if not r.ok:
                fails += 1
        except Exception:
            fails += 1
    assert fails >= int(limit * 0.8), f"only caught {fails}/{limit} body mutations"


def test_c3_roundtrip():
    turns = json.loads((FIXTURES / "c1-turns.json").read_text(encoding="utf-8"))

    for t in turns:
        b = serialize(t)
        recovered = deserialize(b)
        assert canonical(t) == canonical(recovered)

    priv, pub = _gen_keypair()
    unsigned = seal_chain(turns[:5])
    for s in unsigned:
        b = serialize(s)
        recovered = deserialize(b)
        assert canonical(s) == canonical(recovered)

    signed = seal_chain(turns[:5], SignOpts(privkey=priv, pubkey=pub))
    for s in signed:
        b = serialize(s)
        recovered = deserialize(b)
        assert canonical(s) == canonical(recovered)


def test_c4_chain_tamper():
    priv, pub = _gen_keypair()

    def mk(i: int, content: str):
        return {
            "version": "scroll/0.1",
            "turn": i,
            "role": "user" if i % 2 == 0 else "assistant",
            "model": {"vendor": "anthropic", "id": "claude-sonnet-4-5"},
            "params": {"temperature": 0, "top_p": 1},
            "messages": [{"role": "user" if i % 2 == 0 else "assistant", "content": content}],
            "timestamp_ns": 1700000000000000000 + i,
        }

    raw = [mk(i, f"msg{i}") for i in range(5)]
    chain = seal_chain(raw, SignOpts(privkey=priv, pubkey=pub))
    assert len(chain) == 5
    base = verify(chain, pub)
    assert base.ok, base.failures

    swapped = [chain[0], chain[2], chain[1], chain[3], chain[4]]
    assert not verify(swapped, pub).ok

    t3_mut = {**chain[3], "prev_hash": "sha256:" + "a" * 64}
    broken_prev = [chain[0], chain[1], chain[2], t3_mut, chain[4]]
    assert not verify(broken_prev, pub).ok

    t2_mut = {**chain[2], "hash": "sha256:" + "b" * 64}
    broken_hash = [chain[0], chain[1], t2_mut, chain[3], chain[4]]
    assert not verify(broken_hash, pub).ok


@pytest.mark.parametrize(
    "vector_path",
    sorted((Path(__file__).resolve().parent.parent / "vectors").glob("*.json")),
    ids=lambda p: p.stem,
)
def test_vector_schema_parse(vector_path: Path):
    """Every wire-format vector must parse as a valid SealedTurn array."""
    from agent_scroll.schema import validate_sealed_turn

    data = json.loads(vector_path.read_text(encoding="utf-8"))
    assert isinstance(data, list) and len(data) >= 1
    for item in data:
        ok, err = validate_sealed_turn(item)
        assert ok, f"{vector_path.name}: {err}"
