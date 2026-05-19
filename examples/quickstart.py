"""agent-scroll quickstart — build a 3-turn signed chain, verify, then tamper."""

from __future__ import annotations

import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from agent_scroll import SignOpts, seal_chain, verify

# 1. Generate an Ed25519 keypair.
sk = Ed25519PrivateKey.generate()
raw = serialization.Encoding.Raw
priv = sk.private_bytes(encoding=raw, format=serialization.PrivateFormat.Raw,
                        encryption_algorithm=serialization.NoEncryption())
pub = sk.public_key().public_bytes(encoding=raw, format=serialization.PublicFormat.Raw)

# 2. Build three plain turns. timestamp_ns differs so each turn hashes uniquely.
base = {
    "version": "scroll/0.1",
    "model": {"vendor": "anthropic", "id": "claude-opus-4-7"},
    "params": {"temperature": 0, "top_p": 1},
}
turns = [
    {**base, "turn": 0, "role": "user",
     "messages": [{"role": "user", "content": "What is the capital of France?"}],
     "timestamp_ns": 1_700_000_000_000_000_000},
    {**base, "turn": 1, "role": "assistant",
     "messages": [{"role": "assistant", "content": "Paris."}],
     "timestamp_ns": 1_700_000_000_000_000_001},
    {**base, "turn": 2, "role": "user",
     "messages": [{"role": "user", "content": "Thanks!"}],
     "timestamp_ns": 1_700_000_000_000_000_002},
]

# 3. Seal + sign as a chain. seal_chain links each turn via prev_hash.
chain = seal_chain(turns, SignOpts(privkey=priv, pubkey=pub))
print(f"sealed {len(chain)} turns, all hashes set")

# 4. Verify the clean chain.
clean = verify(chain, pub)
print(f"verify clean: ok={clean.ok}")

# 5. Tamper: replace one hex char in turn[1]'s hash.
tampered = [dict(t) for t in chain]
h = tampered[1]["hash"]
tampered[1]["hash"] = h[:-1] + ("0" if h[-1] != "0" else "f")

bad = verify(tampered, pub)
print(f"verify tampered: ok={bad.ok} reason={bad.failures[0].reason}")

# Optional: dump the chain as canonical JSON for inspection.
_ = json.dumps(chain, indent=2)
