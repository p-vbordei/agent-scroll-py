# Architecture — agent-scroll-py

## Goal

Port the [`agent-scroll`](https://github.com/p-vbordei/agent-scroll) v0.1 specification to idiomatic Python with byte-identical output to the TypeScript reference. The contract is the conformance vector set: same JCS bytes, same SHA-256 hashes, same Ed25519 signatures, verified by `tests/test_conformance.py`.

## Module map

| Python module | TS counterpart | Responsibility |
|---|---|---|
| `agent_scroll.canonical` | `src/canonical.ts` | `canonical(value)` → JCS bytes; `hash_canonical(value)` → `sha256:<hex>` string |
| `agent_scroll.schema` | `src/schema.ts` | `Turn`/`SealedTurn` TypedDicts, `validate_turn`/`validate_sealed_turn` (hand-rolled, no Zod equivalent needed) |
| `agent_scroll.seal` | `src/seal.ts` | `seal(turn, sign?)` and `seal_chain(turns, sign?)` — hash, link via `prev_hash`, optionally Ed25519-sign |
| `agent_scroll.verify` | `src/verify.ts` | `verify(chain, pubkey?)` → `VerifyResult` with failures `BadHash` / `BrokenChain` / `BadSignature` / `SchemaViolation` |
| `agent_scroll.serialize` | (in `index.ts`) | `serialize` / `deserialize` round-trip through canonical bytes |
| `agent_scroll.__init__` | `src/index.ts` | Public barrel |

CLI is intentionally not ported — the TS reference's `scroll` CLI is a developer convenience, not part of the wire format.

## Dependency choices

| Concern | Library | Why |
|---|---|---|
| JCS encoding | [`jcs`](https://pypi.org/project/jcs/) | RFC 8785 implementation; matches TS `canonicalize`. Python `int` keeps full precision so `timestamp_ns` flows through verbatim — no `u64 → f64` workaround needed (unlike Rust). |
| Hashing | `hashlib.sha256` (stdlib) | Universal. |
| Ed25519 | [`cryptography`](https://pypi.org/project/cryptography/) | `Ed25519PrivateKey.sign(...)` / `Ed25519PublicKey.verify(...)`. Raw 32-byte seeds match the TS `nacl.sign.keyPair` shape. |
| Base64 | `base64` (stdlib) | Standard alphabet, matches TS. |

Schema validation is hand-rolled (no Pydantic / Zod) to keep the dependency surface minimal and produce identical error semantics to the TS Zod errors.

## Byte-determinism invariants

The whole library is one big purity boundary: same input → same canonical bytes → same hash → same signature (modulo Ed25519's deterministic nonce).

1. **Canonical bytes.** `canonical(turn)` MUST equal the TS reference's `canonical(turn)` byte-for-byte. Verified by C1 across 20 vectors.
2. **Hash strings.** `hash_canonical(turn)` returns `sha256:<lowercase hex>` — always lowercase, always 64 hex chars.
3. **Signature bytes.** Ed25519 over `canonical(turn)` (the unsealed turn — no `hash`, no `sig` keys), base64-standard encoded.
4. **Roundtrip stability.** `canonical(deserialize(serialize(t)))` == `canonical(t)`. JCS sorts object keys, so re-encoding a parsed object is idempotent.
5. **Chain link.** `chain[i].prev_hash == chain[i-1].hash` for `i ≥ 1`. Turn 0 omits `prev_hash`.

## Testing strategy

`tests/test_conformance.py` mirrors the TS `conformance/runner.ts`:

- **C1 byte-equality** — load `fixtures/c1-turns.json` (20 turns) and `fixtures/c1-hex.json` (expected hex bytes); assert `canonical(t).hex() == expected[k]` for every k. This is the single load-bearing test — if it passes, the wire format is correct.
- **C2 mutation** — seal a turn, then (A) flip every hex char of the hash and (B) XOR `0x80` over the first 256 body bytes; `verify` MUST reject every variant.
- **C3 roundtrip** — `serialize` → `deserialize` for plain turns, unsigned sealed turns, and signed sealed turns; canonical bytes must match before and after.
- **C4 chain tamper** — build a 5-turn signed chain, then mutate it three ways: swap order, replace `prev_hash`, replace `hash`. All variants MUST fail `verify`.
- **Schema parse** — every JSON in `vectors/` must `validate_sealed_turn` cleanly.

Adding a new C1 vector requires adding to BOTH `fixtures/c1-turns.json` and `fixtures/c1-hex.json` (with the hex generated from the TS reference, not from this port).
